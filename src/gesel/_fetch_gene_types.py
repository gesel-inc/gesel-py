from typing import Optional

from . import _new_config as cfg
from ._fetch_gene_version import fetch_gene_version


def fetch_gene_types(
    species: str,
    config: Optional[dict] = None
) -> list:
    """
    Fetch the list of available gene identifier types for this species.

    In older versions (0.1.0) of the Gesel gene annotation file specification, an explicit listing of types was not generated.
    This function will just assume that `ensembl`, `entrez` and `symbol` are  available.

    Args:
        species:
            Taxonomy ID of the species of interest.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        List of strings containing the gene identifier types available to ``species``.

    Examples:
        >>> import gesel
        >>> gesel.fetch_gene_types("9606")
        >>> gesel.fetch_gene_types("10090")
    """

    config = cfg._get_config(config)
    if fetch_gene_version(species, config = config) == "0.1.0":
        return ["ensembl", "entrez", "symbol"]

    cached = cfg._get_cache(config, "fetch_gene_types", species)
    if cached is not None:
        return cached

    manifest = cfg._fetch_gene(config, species + "_gene-types.tsv")
    types = []
    with open(manifest, "r") as handle:
        for line in handle:
            types.append(line.rstrip())

    cfg._set_cache(config, "fetch_gene_types", species, types)
    return types
