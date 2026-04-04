from typing import Optional
import biocframe
import biocutils

from . import _new_config as cfg
from ._fetch_all_sets import _compute_set_to_collection_indices 
from ._fetch_some_collections import fetch_collection_sizes


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
        A :py:func:`~biocframe.BiocFrame` with the same columns as that returned by :py:func:`~gesel.fetch_all_sets`,
        where each row corresponds to an entry of ``sets``.

    Examples:
        >>> import gesel
        >>> gesel.fetch_some_sets("9606", [0, 10, 20])
    """

    config = cfg.get_config(config)
    candidate = cfg.get_cache(config, "fetch_all_sets", species)
    if candidate is not None:
        output = candidate[sets,:]
        return output

    fname = species + "_sets.tsv"
    cached, modified = _get_single_set_ranges(config, species, fname)
    prior_sets = cached["prior"]["sets"]
    prior_details = cached["prior"]["details"]

    # TODO: move this to biocutils as setdiff().
    needed = []
    already_present = set(prior_sets)
    for s in sets:
        if s not in already_present:
            needed.append(s)

    if len(needed) > 0:
        intervals = cached["intervals"]
        starts = []
        ends = []
        for s in needed:
            starts.append(intervals[s])
            ends.append(intervals[s + 1] - 1) # remove the newline

        deets = cfg.fetch_ranges(config, fname, starts, ends)
        name = []
        desc = []
        for d in deets:
            split = d.decode("utf-8").split("\t")
            name.append(split[0])
            desc.append(split[1])

        extra_df = biocframe.BiocFrame({ "name": name, "description": desc })
        prior_details = biocutils.combine_rows(prior_details, extra_df)
        prior_sets += needed
        modified = True

    if modified:
        cached["prior"]["sets"] = prior_sets
        cached["prior"]["details"] = prior_details
        cfg.set_cache(config, "fetch_some_sets", species, cached)

    output = prior_details[biocutils.match(sets, prior_sets),:]
    output = output.set_column("size", biocutils.subset(cached["sizes"], sets))
    output = output.set_column("collection", biocutils.subset(cached["collections"], sets))
    output = output.set_column("number", biocutils.subset(cached["numbers"], sets))
    return output


def _get_single_set_ranges(config: dict, species: str, fname: str) -> tuple:
    cached = cfg.get_cache(config, "fetch_some_sets", species)
    if cached is not None:
        return cached, False

    ranges, sizes = cfg._retrieve_ranges_with_sizes(config, fname)
    coll_sizes = fetch_collection_sizes(species, config=config)
    collections, numbers = _compute_set_to_collection_indices(coll_sizes)
    cached = {
        "intervals": ranges,
        "collections": collections,
        "numbers": numbers,
        "sizes": sizes,
        "prior": { 
            "sets": [],
            "details": biocframe.BiocFrame({ "name": [], "description": [] })
        }
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

    config = cfg.get_config(config)
    candidate = cfg.get_cache(config, "fetch_all_sets", species)
    if candidate is not None:
        return candidate["size"]

    fname = species + "_sets.tsv"
    cached, modified = _get_single_set_ranges(config, species, fname)
    if modified:
        cfg.set_cache(config, "fetch_some_sets", species, cached)

    return cached["sizes"]
