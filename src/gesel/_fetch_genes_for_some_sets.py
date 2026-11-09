from typing import Optional
import biocutils

from . import _new_config as cfg
from . import _utils as utils
from . import _consolidate_ranges as cons


def fetch_genes_for_some_sets(species: str, sets: list, config: Optional[dict] = None) -> list:
    """
    Fetch the gene membership for some sets in the Gesel database.
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
        >>> some_sets = gesel.fetch_genes_for_some_sets("9606", [0, 10, 20])
        >>> len(some_sets)
        >>> first_set = some_sets[0]
        >>> print(first_set)
        >>>
        >>> # Genes in the first set:
        >>> gene_symbols = gesel.fetch_all_genes("9606")["symbol"]
        >>> import biocutils
        >>> biocutils.subset(gene_symbols, first_set)
        >>>
        >>> # Identities of the sets used above.
        >>> set_info = gesel.fetch_all_sets("9606")
        >>> print(set_info[[0, 10, 20], :])
    """

    config = cfg._get_config(config)
    candidate = cfg._get_cache(config, "fetch_genes_for_all_sets", species)
    if candidate is not None:
        return biocutils.subset(candidate, sets)

    fname = species + "_set2gene.tsv"
    cached = cfg._get_cache(config, "fetch_genes_for_some_sets", species)
    modified = False

    if cached is None:
        intervals = cfg._retrieve_ranges(config, fname)
        cached = {
            "range_boundaries": intervals,
            "block_info": cons._define_blocks(intervals, cons._retrieve_consolidate_block_size(config)),
            "prior": {}
        }
        modified = True

    priors = cached["prior"]
    needed = []
    for s in sets:
        if s not in priors:
            needed.append(s)

    if len(needed) > 0:
        modified = True
        requested_ranges, deets = cons._fetch_consolidated_ranges(config, fname, cached["range_boundaries"], cached["block_info"], needed)
        for r, line in zip(requested_ranges, deets):
            priors[r] = utils._decode_indices(line)

    if modified:
        # Technically not necessary as these were modified by reference, but let's just set them to be safe.
        cached["prior"] = priors
        cfg._set_cache(config, "fetch_genes_for_some_sets", species, cached)

    output = []
    for s in sets:
        output.append(priors[s])
    return output
