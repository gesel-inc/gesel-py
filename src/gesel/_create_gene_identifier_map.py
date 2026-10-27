from typing import Optional

from . import _new_config as cfg
from ._fetch_all_genes import fetch_all_genes


def create_gene_identifier_map(
    species: str,
    type: str,
    ignore_case: bool = False,
    config: Optional[dict] = None
) -> dict:
    """
    Create a mapping of gene identifiers (Ensembl, symbol, etc.) to their gene indices.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        type:
            Type of gene identifier.
            Typically one of ``symbol``, ``entrez``, and/or ``ensembl``.

        ignore_case:
            Whether case should be ignored when creating the mapping.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        Dictionary where each key is the gene identifier of the specified ``type`` and each value is a list of integers.
        Each list contains the indices of genes associated with that identifier (after ignoring case, if ``ignore_case = True``).
        List entries should be interpreted as row indices into the data frame returned by :py:func:`~gesel.fetch_all_genes`.

    Examples:
        >>> import gesel
        >>> mapping = gesel.create_gene_identifier_map("9606", type="symbol")
        >>>
        >>> # Taking it for a spin:
        >>> found = mapping["SNAP25"]
        >>> print(found)
        >>>
        >>> # Cross-checking it
        >>> ref = gesel.fetch_all_genes("9606")["symbol"]
        >>> import biocutils
        >>> biocutils.subset(ref, found)
    """

    if ignore_case:
        store_name = "lower"
    else:
        store_name = "cased"

    config = cfg._get_config(config)
    cached = cfg._get_cache(config, "create_gene_identifier_map", species)

    modified = False
    if cached is None:
        cached = {}

    if store_name in cached:
        sfound = cached[store_name]
        modified = False 
    else:
        sfound = {} 
        modified = True 

    if type in sfound:
        tfound = sfound[type]
    else:
        tfound = {}
        modified = True

        genes = fetch_all_genes(species, types=[type], config=config)[type]
        for i, names in enumerate(genes):
            for n in names:
                if ignore_case:
                    nm = n.lower()
                else:
                    nm = n
                if nm in tfound:
                    tfound[nm].add(i)
                else:
                    tfound[nm] = set([i])

        for k, v in tfound.items():
            tfound[k] = list(v)

    if modified:
        sfound[type] = tfound
        cached[store_name] = sfound
        cfg._set_cache(config, "create_gene_identifier_map", species, cached)

    return tfound


def map_genes_by_name(
    species: str,
    type: str,
    ignore_case: bool = False,
    config: Optional[dict] = None
) -> dict:
    """Deprecated, use :py:func:`~create_gene_identifier_map` instead."""
    return create_gene_identifier_map(species, type, ignore_case=ignore_case, config=config)
