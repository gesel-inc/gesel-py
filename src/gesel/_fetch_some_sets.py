from typing import Optional
import biocframe
import biocutils

from . import _new_config as cfg
from ._fetch_all_sets import _compute_set_to_collection_indices 
from ._fetch_some_collections import fetch_collection_sizes
from . import _consolidate_ranges as cons


def fetch_some_sets(
    species: str,
    sets: list,
    config: Optional[dict] = None
) -> biocframe.BiocFrame:
    """
    Fetch the details of some gene sets from the Gesel database.
    This can be more efficient than :py:func:`~gesel.fetch_all_sets` when only a few sets are of interest.

    Every time this function is called, information from the requested ``sets`` will be added to an in-memory cache.
    Subsequent calls to this function will re-use as many of the cached sets as possible.

    If :py:func:`~gesel.fetch_all_sets` was previously called, information from all sets are cached in memory and will be retrieved when this function is called.
    If ``sets`` is large, it may be beneficial to call :py:func:`~gesel.fetch_all_sets` first before calling this function.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        sets:
            List of set indices, where each set index refers to a row in the data frame returned by :py:func:`~gesel.fetch_all_sets`.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        A :py:class:`~biocframe.BiocFrame` with the same columns as that returned by :py:func:`~gesel.fetch_all_sets`,
        where each row corresponds to an entry of ``sets``.

    Examples:
        >>> import gesel
        >>> gesel.fetch_some_sets("9606", [0, 10, 20])
    """

    config = cfg._get_config(config)
    candidate = cfg._get_cache(config, "fetch_all_sets", species)
    if candidate is not None:
        output = candidate[sets,:]
        return output

    fname = species + "_sets.tsv"
    cached, modified = _get_single_set_ranges(config, species, fname)
    priors = cached["prior"]

    needed_sets = []
    for s in sets:
        if s not in priors:
            needed_sets.append(s)

    if len(needed_sets) > 0:
        modified = True
        requested_ranges, deets = cons._fetch_consolidated_ranges(config, fname, cached["range_boundaries"], cached["block_info"], needed_sets)
        for r, line in zip(requested_ranges, deets):
            split = line.decode("utf-8").split("\t")
            priors[r] = (split[0], split[1])

    if modified:
        # Technically not necessary as these were modified by reference, but let's just set them to be safe.
        cached["prior"] = priors
        cfg._set_cache(config, "fetch_some_sets", species, cached)

    output_names = []
    output_descriptions = []
    for s in sets:
        name, desc = priors[s]
        output_names.append(name)
        output_descriptions.append(desc)

    return biocframe.BiocFrame({
        "name": output_names,
        "description": output_descriptions, 
        "size": biocutils.subset(cached["sizes"], sets),
        "collection": biocutils.subset(cached["collections"], sets),
        "number": biocutils.subset(cached["numbers"], sets)
    })


def _get_single_set_ranges(config: dict, species: str, fname: str) -> tuple:
    cached = cfg._get_cache(config, "fetch_some_sets", species)
    if cached is not None:
        return cached, False

    ranges, sizes = cfg._retrieve_ranges_with_sizes(config, fname)
    coll_sizes = fetch_collection_sizes(species, config=config)
    collections, numbers = _compute_set_to_collection_indices(coll_sizes)
    cached = {
        "range_boundaries": ranges,
        "block_info": cons._define_blocks(ranges, block_size = cons._retrieve_consolidate_block_size(config)),
        "collections": collections,
        "numbers": numbers,
        "sizes": sizes,
        "prior": {}
    }

    return cached, True


def fetch_set_sizes(species: str, config: Optional[dict] = None) -> list:
    """
    Quickly get the sizes of the sets in the Gesel database.
    This is more efficient than :py:func:`~gesel.fetch_all_sets` when only the sizes are of interest.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        List containing the size of each set (i.e., the number of genes in each set).

    Examples:
        >>> import gesel
        >>> gesel.fetch_set_sizes("9606")
    """

    config = cfg._get_config(config)
    candidate = cfg._get_cache(config, "fetch_all_sets", species)
    if candidate is not None:
        return candidate["size"]

    fname = species + "_sets.tsv"
    cached, modified = _get_single_set_ranges(config, species, fname)
    if modified:
        cfg._set_cache(config, "fetch_some_sets", species, cached)

    return cached["sizes"]
