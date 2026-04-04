from typing import Optional
import biocutils

from . import _new_config as cfg
from . import _utils as utils

def fetch_genes_for_some_sets(species: str, sets: list, config: Optional[dict] = None) -> list:
    """
    Fetch genes for some sets in the Gesel database.
    This can be more efficient than :py:func:`~gesel.fetch_genes_for_all_sets` if only a few sets are of interest.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        sets:
            List of set indices, where each set index refers to a row in the data frame returned by :py:func:`~gesel.fetch_all_sets`.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        List of integer vectors.
        Each vector corresponds to a set in ``sets`` and contains the identities of its member genes.
        Each gene is defined by its gene index, which refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_genes`.

    Examples:
        >>> import gesel
        >>> first_set = gesel.fetch_genes_for_some_sets("9606", [0, 10, 20])
        >>> len(first_set)
        >>> first_set[0]
        >>>
        >>> # Genes in the first set:
        >>> gene_symbols = gesel.fetch_all_genes("9606")["symbol"]
        >>> import biocutils
        >>> biocutils.subset(gene_symbols, first_set[0])
        >>>
        >>> # Identities of the sets used above.
        >>> set_info = gesel.fetch_all_sets("9606")
        >>> print(set_info[[0, 10, 20], :])
    """

    config = cfg.get_config(config)
    candidate = cfg.get_cache(config, "fetch_genes_for_all_sets", species)
    if candidate is not None:
        return biocutils.subset(candidate, sets)

    fname = species + "_set2gene.tsv"
    cached = cfg.get_cache(config, "fetch_genes_for_some_sets", species)
    modified = False

    if cached is None:
        intervals  = cfg._retrieve_ranges(config, fname)
        cached = {
            "intervals": intervals,
            "prior": {
                "set": [],
                "genes": []
            }
        }
        modified = True

    prior_set = cached["prior"]["set"]
    prior_genes = cached["prior"]["genes"]

    # TODO: move this to biocutils as setdiff().
    needed = []
    already_present = set(prior_set)
    for s in sets:
        if s not in already_present:
            needed.append(s)

    if len(needed) > 0:
        intervals = cached["intervals"]
        starts = []
        ends = []
        for s in needed:
            starts.append(intervals[s])
            ends.append(intervals[s + 1])
        deets = cfg.fetch_ranges(config, fname, starts, ends)
        for line in deets:
            prior_genes.append(utils._decode_indices(line))
        prior_set += needed
        modified = True

    if modified:
        # Technically not necessary as these were modified by reference, but let's just set them to be safe.
        cached["prior"]["set"] = prior_set
        cached["prior"]["genes"] = prior_genes
        cfg.set_cache(config, "fetch_genes_for_some_sets", species, cached)

    m = biocutils.match(sets, prior_set)
    return biocutils.subset(prior_genes, m)
