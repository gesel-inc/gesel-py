from ._download_database_file import database_url
from . import _utils as utils
from typing import Optional
import requests


def download_database_ranges(
    name: str,
    start: list[int],
    end: list[int],
    url: Optional[str] = None,
    multipart: bool = False
) -> list[str]:
    """
    Download any number of byte ranges from a Gesel database file.

    Args:
        name:
            Name of the file.
            This usually has the species identifier as a prefix.

        start:
            List of integers containing the zero-indexed closed start of each byte range to extract from the file.
            This list may be empty.

        end:
            List of integers containing the zero-indexed open end of each byte range to extract from the file.
            This should have the same length as ``start`` such that the ``i``-th range is defined as ``[start[i], end[i])``.
            All ranges supplied in a single call to this function should be non-overlapping.

        url:
            Base URL to the Gesel database files.
            If ``None``, it is set to :py:func:`~download_database_file.database_url`.

        multipart:
            Whether the server at ``url`` supports multi-part range requests.

    Returns:
        List of byte strings containing the requested bytes for each range.
        For ranges where ``end <= start``, an empty string is returned.

    Examples:
        >>> import gesel
        >>> gesel.download_database_ranges("9606_set2gene.tsv", [0], [100])
        >>> gesel.download_database_ranges("9606_set2gene.tsv", [10, 100, 1000], [20, 150, 1100])
    """

    if url is None:
        url = database_url()
    url = url + "/" + name

    if multipart:
        return download_multipart_ranges(url, start, end)

    output = [b""] * len(start)
    for i in range(len(start)):
        curstart = start[i]
        curend = end[i]
        if curend <= curstart:
            continue

        resp = requests.get(url, headers = { "Range": "bytes=" + str(curstart) + "-" + str(curend - 1) }) # byte ranges are closed intervals, not half-open.
        if resp.status_code >= 300:
            raise utils.format_error(resp)

        # We use 'content' instead of 'text' to handle multi-byte characters correctly.
        output[i] = resp.content[:(curend - curstart)]

    return output


def download_multipart_ranges(
    url: str,
    start: list[int],
    end: list[int],
    _mock = None
) -> list[str]:
    """
    Perform a multi-part range request on a Gesel database file.

    Args:
        url:
            URL to a specific Gesel database file.

        start:
            List of integers containing the zero-indexed closed start of each byte range to extract from the file.
            This list may be empty.

        end:
            List of integers containing the zero-indexed open end of each byte range to extract from the file.
            This should have the same length as ``start`` such that the ``i``-th range is defined as ``[start[i], end[i])``.
            All ranges supplied in a single call to this function should be non-overlapping.

        _mock:
            Internal use only.

    Returns:
        List of byte strings containing the requested bytes for each range.
        For ranges where ``end <= start``, an empty string is returned.

    Examples:
        >>> import gesel
        >>> url = gesel.database_url() + "/9606_set2gene.tsv" 
        >>> gesel.download_multipart_ranges(url, [0], [100])
        >>> gesel.download_multipart_ranges(url, [10, 100, 1000], [10, 150, 900])
        >>> # Note: as of writing, GitHub releases don't support multi-part range requests.
    """

    collected = []
    for i in range(len(start)):
        curstart = start[i]
        curend = end[i]
        if curend <= curstart:
            continue
        collected.append((curstart, curend, i))
    collected.sort()

    output = [b""] * len(start)
    if len(collected) == 0:
        return output

    formatted = []
    for curstart, curend, _ in collected:
        formatted.append(str(curstart) + "-" + str(curend - 1)) # byte ranges are closed intervals, not half-open.

    if _mock is None:
        resp = requests.get(url, headers = { "Range": "bytes=" + ", ".join(formatted) })
    else:
        resp = _mock(url, "bytes=" + ", ".join(formatted)) 
    if resp.status_code >= 300:
        raise utils.format_error(resp)

    if len(collected) == 1:
        curstart, curend, curi = collected[0]
        output[curi] = resp.content[:(curend - curstart)]
        return output

    ct = resp.headers["Content-Type"]
    prefix = "multipart/byteranges; boundary="
    if not ct.startswith(prefix):
        raise RuntimeError("unexpected content type from multi-part range request")
    boundary = ct[len(prefix):]

    # Remember, we operate on the byte strings to correctly handle ranges for multi-byte characters.
    parsed_start, parsed_content = _parse_multipart_response(resp.content, boundary.encode("utf-8"))
    import bisect
    for curstart, curend, curi in collected:
        chosen = bisect.bisect_right(parsed_start, curstart) - 1
        offset = parsed_start[chosen]
        output[curi] = parsed_content[chosen][(curstart - offset):(curend - offset)]

    return output


# WARNING: this part only works when the contents of body are fully string-able;
# otherwise, if it's binary data, we really should be working with them as raw data.
def _parse_multipart_response(body: bytes, boundary: bytes) -> tuple[list, list]:
    position = 0
    boundary = b"--" + boundary
    starts = []
    contents = []

    while True:
        if body[position:(position + len(boundary))] != boundary:
            raise RuntimeError("missing boundary in multi-part range request")
        position += len(boundary)

        remaining = body[position:(position + 2)]
        if remaining == b"--":
            break 
        if remaining != b"\r\n":
            raise RuntimeError("unexpected content range format in multi-part response")
        position += 2

        # Running through all headers. 
        headers = {}
        while True:
            crlf = body.find(b"\r\n", position)
            if crlf == -1:
                raise RuntimeError("failed to find CRLF to terminate headers in multi-part response")
            curline = body[position:crlf]
            position = crlf + 2
            if curline == b"": # headers terminate at a CRLF empty line.
                break 
            at_colon = curline.find(b":")
            headers[curline[:at_colon].lower()] = curline[(at_colon+1):]

        if b"content-range" not in headers:
            raise RuntimeError("expected a 'content-range' header in each multi-part response")
        crange = headers[b"content-range"]
        to_bytes = crange.find(b"bytes ")
        to_dash = crange.find(b"-")
        to_slash = crange.find(b"/")
        if to_bytes == -1 or to_dash == -1 or to_slash == -1 or to_dash >= to_slash:
            raise RuntimeError("expected 'content-range' header to follow a 'bytes <start>-<end>/<size>' format")

        first = int(crange[(to_bytes + 6):to_dash])
        last = int(crange[(to_dash + 1):to_slash])
        starts.append(first) 
        curlen = last - first + 1
        contents.append(body[position:(position + curlen)])
        position += curlen 

        remaining = body[position:(position + 2)]
        if remaining != b"\r\n":
            raise RuntimeError("expected a newline after each part of a multi-part response")
        position += 2

    return starts, contents
