from typing import Optional

from . import _new_config as cfg
from ._map_genes_by_name import map_genes_by_name


def search_genes(
    species: str,
    genes: list,
    types: list = ["entrez", "ensembl", "symbol"],
    ignore_case: bool = True,
    config: Optional[dict] = None
) -> list:
    """
    Search for genes by converting gene identifiers to gene indices.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        genes:
            List of gene names of any type specified in ``types``.

        types:
            Types of gene names to return.
            Typically one or more of ``symbol``, ``entrez``, and/or ``ensembl``.

        ignore_case:
            Whether case should be ignored when creating the mapping.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        List of length equal to ``genes``.
        Each entry is an integer vector of gene indices that refer to rows of the data frame returned by :py:func:`~gesel.fetch_all_genes`.
        These rows represent the genes that match to the corresponding entry of ``genes``.

    Examples:
        >>> import gesel
        >>> out = gesel.search_genes("9606", ["SNAP25", "NEUROD6", "ENSG00000139618"])
        >>> print(out)
        >>>
        >>> # Round-tripping them:
        >>> genes = gesel.fetch_all_genes("9606")
        >>> print(genes[out[0],:])
        >>> print(genes[out[1],:])
        >>> print(genes[out[2],:])
    """

    if ignore_case:
        genes = [g.lower() for g in genes]

    output = []
    for i in range(len(genes)):
        output.append([])

    for t in types:
        mappings = map_genes_by_name(species, t, ignore_case=ignore_case, config=config)
        for i, g in enumerate(genes):
            if g in mappings:
                output[i] += mappings[g]

    return output
