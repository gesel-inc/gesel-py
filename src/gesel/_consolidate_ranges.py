from typing import Optional
import biocutils

from ._new_config import _fetch_ranges


_consolidate_block_size = 10000


def consolidate_block_size(block_size: Optional[int] = None) -> int:
    """
    Get or set the block size for consolidating HTTP range requests.

    Each file is split up into blocks of size approximately equal to ``block_size``.
    When performing a range request, all ranges in the same block will be retrieved. 
    This consolidates near-adjacent ranges into a single request, reducing the number of requests at the cost of increasing the size of each request.

    All ranges associated with a block will be cached in memory, even those that were not directly requested.
    Subsequent function calls can then quickly retrieve ranges from this cache instead of making a new HTTP request. 
    Downloading and caching the entire block also ensures that the same bytes will never be requested from the server twice in the same session.

    Setting the block size to a value of 1 indicates that no consolidation is to be performed, i.e., each range is requested as-is.

    Args:
        block_size:
            Block size in bytes.
            Larger sizes reduce the number of requests at the cost of increasing the size of each request.

    Returns:
        If ``block_size = None``, the current block size is returned.

        If ``block_size`` is provided, it is used to set the block size, and the previous value is returned. 

    Examples:
        >>> import gesel
        >>> gesel.consolidate_block_size()
        >>> old = gesel.consolidate_block_size(500)
        >>> gesel.consolidate_block_size()
        >>> gesel.consolidate_block_size(old)
    """

    global _consolidate_block_size
    if block_size is None:
        return _consolidate_block_size
    else:
        previous = _consolidate_block_size
        _consolidate_block_size = block_size
        return previous


def _retrieve_consolidate_block_size(config: dict) -> int:
    cbs = config["consolidate_block_size"]
    if cbs is None:
        cbs = consolidate_block_size()
    return cbs


def _define_blocks(range_boundaries: list, block_size: int) -> dict:
    block_ids = []
    for i in range(1, len(range_boundaries)):
        curstart = range_boundaries[i - 1]
        curend = range_boundaries[i]
        curmid = curstart + (curend - curstart) * 0.5 # use midpoints to place blocks
        block_ids.append(int(curmid / block_size))

    if len(block_ids):
        block_ids = biocutils.Factor.from_sequence(block_ids).get_codes() # force all IDs to be consecutive.
        block_boundaries = [range_boundaries[0]]
        for i in range(1, len(block_ids)):
            if block_ids[i] != block_ids[i-1]:
                block_boundaries.append(range_boundaries[i])
        block_boundaries.append(range_boundaries[-1])
    else:
        block_boundaries = []

    ranges_by_block = []
    if len(block_ids):
        for i in range(block_ids[-1] + 1): # i.e., the largest value.
            ranges_by_block.append([])
        for i, r in enumerate(block_ids):
            ranges_by_block[r].append(i)

    return block_boundaries, block_ids, ranges_by_block


def _consolidate_ranges_by_block(block_info: tuple, needed_ranges: list) -> dict:
    block_boundaries, block_ids, ranges_by_block = block_info

    requested_blocks = set()
    for rg in needed_ranges:
        requested_blocks.add(block_ids[rg])

    requested_blocks = list(requested_blocks)
    requested_blocks.sort()
    if len(requested_blocks) == 0:
        return { "start": [], "end": [], "requested": [] }

    requested_ranges = [] + ranges_by_block[requested_blocks[0]]
    consolidated_starts = [block_boundaries[requested_blocks[0]]]
    consolidated_ends = []
    for i in range(1, len(requested_blocks)):
        previous_block = requested_blocks[i - 1]
        next_block = requested_blocks[i]
        if next_block - previous_block > 1:
            consolidated_ends.append(block_boundaries[previous_block + 1])
            consolidated_starts.append(block_boundaries[next_block])
        requested_ranges += ranges_by_block[requested_blocks[i]]
    consolidated_ends.append(block_boundaries[requested_blocks[-1] + 1])

    return consolidated_starts, consolidated_ends, requested_ranges 


def _extract_ranges_from_consolidated_output(consolidated_output: tuple, requested_start: list, requested_end: list) -> list:
    RETBYTES = 0
    RETSTART = 1
    RETEND = 2

    is_unsorted = False
    nretrieved = len(consolidated_output)
    for i in range(1, nretrieved):
        if consolidated_output[i][RETSTART] < consolidated_output[i - 1][RETSTART]: 
            is_unsorted = True
            break

    # We only care the start positions are sorted, nested intervals with tied starts are just ignored.
    # So, there's no need to sort by both start and end positions.
    if is_unsorted:
        conolidated_output = sorted(consolidated_output, key = lambda x : x[RETSTART])

    nrequested = len(requested_start)
    for i in range(1, nrequested):
        if requested_start[i] < requested_start[i - 1]:
            raise ValueError("expected 'requested_start' to be sorted")

    output = []
    ret_count = 0;
    for r in range(nrequested):
        cur_req_start = requested_start[r];
        cur_req_end = requested_end[r];

        # Recall that both sets of retrieved/requested ranges are sorted by increasing start position.
        # Our approach is to search for the first retrieved range that encloses our requested range.
        # We only need to pick up from the previous retrieved range because it's impossible for a later requested range to only overlap a previous retrieved range.
        #
        # Specifically, let X_i and Y_i be the start and end of retrieved range i, while P_j and Q_j are the start and end of the requested range j.
        # Let i be the first retrieved range that encloses j, i.e., X_i <= P_j and Y_i >= Q_j but Y_h < Q_j for all h < i.
        # (We know that X_h <= X_i due to sorting, so for h to not enclose j, the end position of j must exceed that of h.)
        # Now, consider a requested range k > j where k is not enclosed by i, i.e., Y_i < Q_k. 
        # (Again, we know that P_j <= P_k due to sorting, so for i to not enclose k, the end position of k must exceed that of i.)
        # This gives us Y_h < Q_j <= Y_i < Q_k, such that it is impossible for any h to enclose k.
        #
        # Note that this logic works with any degree of nesting.
        # If a nested retrieved range is sorted after its parent, it is just ignored, as only the parent will be used.
        # If it's sorted before the parent due to a tied start, then it will be used until its end is exceeded and the algorithm moves onto the parent.
        while ret_count != nretrieved and not (consolidated_output[ret_count][RETSTART] <= cur_req_start and cur_req_end <= consolidated_output[ret_count][RETEND]):
            ret_count += 1;
        if ret_count == nretrieved:
            raise ValueError("failed to find an enclosing byte range for a requested range")

        cur_retrieved = consolidated_output[ret_count]
        cur_offset = cur_retrieved[RETSTART]
        output.append(cur_retrieved[RETBYTES][(cur_req_start - cur_offset):(cur_req_end - cur_offset)])

    return output


def _fetch_consolidated_ranges(config: dict, fname: str, range_boundaries: list, block_info: tuple, needed_ranges: list):
    consolidated_starts, consolidated_ends, requested_ranges = _consolidate_ranges_by_block(block_info, needed_ranges)
    consolidated_output = _fetch_ranges(config, fname, consolidated_starts, consolidated_ends)

    # For back-compatibility.
    if len(consolidated_output) and not isinstance(consolidated_output[0], tuple):
        consolidated_output = [(val, consolidated_starts[i], consolidated_ends[i]) for i, val in enumerate(consolidated_output)]

    requested_start = [] 
    requested_end = [] 
    for r in requested_ranges:
        requested_start.append(range_boundaries[r])
        requested_end.append(range_boundaries[r + 1] - 1) # omit the newline.

    refined = _extract_ranges_from_consolidated_output(consolidated_output, requested_start, requested_end)
    return requested_ranges, refined
