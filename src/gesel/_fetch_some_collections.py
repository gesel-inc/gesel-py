from typing import Optional
import biocframe
import biocutils

from . import _new_config as cfg
from . import _consolidate_ranges as cons


def fetch_some_collections(
    species: str,
    collections: list,
    config: Optional[dict] = None
) -> biocframe.BiocFrame:
    """
    Fetch the details of some gene set collections from the Gesel database.
    This can be more efficient than :py:func:`~gesel.fetch_all_collections` when only a few collections are of interest.

    Every time this function is called, information from the requested ``collections`` will be added to an in-memory cache.
    Subsequent calls to this function will re-use as many of the cached collections as possible.

    If :py:func:`~gesel.fetch_all_collections` was previously called, information from all collections are cached in memory and will be retrieved when this function is called.
    If ``collections`` is large, it may be beneficial to call :py:func:`~gesel.fetch_all_collections` first before calling this function.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        collections:
            List of collection indices.
            Each entry refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_collections`.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        A :py:class:`~biocframe.BiocFrame` with the same columns as that returned by :py:func:`~gesel.fetch_all_collections`,
        where each row corresponds to an entry of ``collections``.

    Examples:
        >>> import gesel
        >>> gesel.fetch_some_collections("9606", [0])
    """

    config = cfg._get_config(config)
    candidate = cfg._get_cache(config, "fetch_all_collections", species)
    if candidate is not None:
        return candidate[collections,:]

    fname = species + "_collections.tsv"
    cached, modified = _get_single_collection_ranges(config, species, fname)
    priors = cached["prior"]

    needed_col = []
    for c in collections:
        if c not in priors:
            needed_col.append(c)

    if len(needed_col) > 0:
        modified = True
        requested_ranges, deets = cons._fetch_consolidated_ranges(config, fname, cached["range_boundaries"], cached["block_info"], needed_col)
        for r, line in zip(requested_ranges, deets):
            split = line.decode("utf-8").split("\t")
            priors[r] = (split[0], split[1], split[3], split[4])

    if modified:
        # Technically not necessary as these were modified by reference, but let's just set them to be safe.
        cached["prior"] = priors
        cfg._set_cache(config, "fetch_some_collections", species, cached)

    output_titles = []
    output_descriptions = []
    output_maintainers = []
    output_sources = []
    for c in collections:
        title, desc, mtr, src = priors[c]
        output_titles.append(title)
        output_descriptions.append(desc)
        output_maintainers.append(mtr)
        output_sources.append(src)

    return biocframe.BiocFrame({
        "title": output_titles,
        "description": output_descriptions,
        "maintainer": output_maintainers,
        "source": output_sources,
        "start": biocutils.subset(cached["starts"], collections),
        "size": biocutils.subset(cached["sizes"], collections)
    })


def _get_single_collection_ranges(config: dict, species: str, fname: str) -> list:
    cached = cfg._get_cache(config, "fetch_some_collections", species)
    if cached is not None:
        return cached, False

    ranges, sizes = cfg._retrieve_ranges_with_sizes(config, fname)
    starts = [0]
    last = 0
    for i in range(len(sizes) -1):
        last += sizes[i]
        starts.append(last)

    cached = {
        "range_boundaries": ranges,
        "block_info": cons._define_blocks(ranges, cons._retrieve_consolidate_block_size(config)),
        "starts": starts,
        "sizes": sizes,
        "prior": {}
    }

    return cached, True


def fetch_collection_sizes(species: str, config: Optional[dict] = None) -> list:
    """
    Quickly get the sizes of the collections in the Gesel database.
    This is more efficient than :py:func:`~gesel.fetch_all_collections` when only the sizes are of interest.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        List containing the size of each collection (i.e., the number of gene sets in each collection).

    Examples:
        >>> import gesel
        >>> gesel.fetch_collection_sizes("9606")
    """

    config = cfg._get_config(config)
    candidate = cfg._get_cache(config, "fetch_all_collections", species)
    if candidate is not None:
        return candidate["size"]

    fname = species + "_collections.tsv"
    cached, modified = _get_single_collection_ranges(config, species, fname)
    if modified:
        cfg._set_cache(config, "fetchSomeCollections", species, cached)

    return cached["sizes"]
