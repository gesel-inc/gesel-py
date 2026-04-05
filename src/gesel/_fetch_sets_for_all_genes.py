from typing import Optional

from . import _new_config as cfg
from . import _utils as utils


def fetch_sets_for_all_genes(species: str, config: Optional[dict] = None) -> list:
    """
    Fetch the identities of the sets that contain each gene in the Gesel database.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        List of lists.
        Each inner list represents a gene, corresponding to the rows of the data frame returned by :py:func:`~gesel.fetch_all_genes`.
        Each inner list contains the identities of the sets that include that gene,
        where each integer is a set index that refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_sets`.

    Examples:
        >>> import gesel
        >>> gene_to_set = gesel.fetch_sets_for_all_genes("9606")
        >>> len(gene_to_set)
        >>> gene_to_set[0]
        >>>
        >>> # Sets containing the first gene.
        >>> set_info = gesel.fetch_all_sets("9606")
        >>> print(set_info[gene_to_set[0],:])
        >>>
        >>> # Identity of the first gene. 
        >>> gene_info = gesel.fetch_all_genes("9606")
        >>> print(gene_info[0,:])
    """

    config = cfg._get_config(config)
    candidate = cfg._get_cache(config, "fetch_sets_for_all_genes", species)
    if candidate is not None:
        return candidate

    fname = species + "_gene2set.tsv.gz"
    path = cfg._fetch_file(config, fname)

    import gzip
    output = []
    with gzip.open(path, "rb") as f:
        for line in f:
            output.append(utils._decode_indices(line))

    cfg._set_cache(config, "fetch_sets_for_all_genes", species, output)
    return output
