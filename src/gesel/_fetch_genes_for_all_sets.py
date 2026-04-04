from typing import Optional

from . import _new_config as cfg
from . import _utils as utils


def fetch_genes_for_all_sets(species: str, config: Optional[dict] = None) -> list:
    """
    Fetch the identities for genes in all sets in the Gesel database.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        List of lists.
        Each inner list represents a gene set, corresponding to the rows of the data frame returned by :py:func:`~gesel.fetch_all_sets`.
        Each inner list contains the identities of the genes in that set, 
        where each integer is a gene index that refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_genes`.

    Examples:
        >>> import gesel
        >>> set_to_gene = gesel.fetch_genes_for_all_sets("9606")
        >>> len(set_to_gene)
        >>> set_to_gene[0]
        >>>
        >>> # Genes in the first set:
        >>> gene_symbols = gesel.fetch_all_genes("9606")["symbol"]
        >>> import biocutils
        >>> biocutils.subset(gene_symbols, set_to_gene[0])
        >>>
        >>> # Identity of the first set. 
        >>> set_info = gesel.fetch_all_sets("9606")
        >>> print(set_info[0,:])
    """

    config = cfg.get_config(config)
    candidate = cfg.get_cache(config, "fetch_genes_for_all_sets", species)
    if candidate is not None:
        return candidate

    fname = species + "_set2gene.tsv.gz"
    path = cfg.fetch_file(config, fname)

    import gzip
    output = []
    with gzip.open(path, "rb") as f:
        for line in f:
            output.append(utils._decode_indices(line))

    cfg.set_cache(config, "fetch_genes_for_all_sets", species, output)
    return output
