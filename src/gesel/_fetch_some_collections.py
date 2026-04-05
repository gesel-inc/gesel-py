from typing import Optional
import biocframe
import biocutils

from . import _new_config as cfg


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
        >>> gesel.fetch_some_collections("9606", 0)
    """

    config = cfg._get_config(config)
    candidate = cfg._get_cache(config, "fetch_all_collections", species)
    if candidate is not None:
        return candidate[collections,:]

    fname = species + "_collections.tsv"
    cached, modified = _get_single_collection_ranges(config, species, fname)
    prior_collections = cached["prior"]["collections"]
    prior_details = cached["prior"]["details"]

    # TODO: move this to biocutils as setdiff().
    needed = []
    already_present = set(prior_collections)
    for c in collections:
        if c not in already_present:
            needed.append(c)

    if len(needed) > 0:
        intervals = cached["intervals"]
        starts = []
        ends = []
        for s in needed:
            starts.append(intervals[s])
            ends.append(intervals[s + 1] - 1) # remove the newline

        deets = cfg._fetch_ranges(config, fname, starts, ends)
        title = []
        desc = []
        maintainer = []
        src = []
        for d in deets:
            split = d.rstrip().decode("utf-8").split("\t")
            title.append(split[0])
            desc.append(split[1])
            maintainer.append(split[3])
            src.append(split[4])

        extra_df = biocframe.BiocFrame({ "title": title, "description": desc, "maintainer": maintainer, "source": src })
        prior_details = biocutils.combine_rows(prior_details, extra_df)
        prior_collections += needed
        modified = True

    if modified:
        cached["prior"]["collections"] = prior_collections
        cached["prior"]["details"] = prior_details
        cfg._set_cache(config, "fetch_some_collections", species, cached)

    output = prior_details[biocutils.match(collections, prior_collections),:]
    output = output.set_column("start", biocutils.subset(cached["starts"], collections))
    output = output.set_column("size", biocutils.subset(cached["sizes"], collections))
    return output


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
        "intervals": ranges,
        "starts": starts,
        "sizes": sizes,
        "prior": {
            "collections": [],
            "details": biocframe.BiocFrame({
                "title": [],
                "description": [],
                "maintainer": [],
                "source": []
            })
        }
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
