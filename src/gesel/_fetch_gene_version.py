from typing import Optional

from . import _new_config as cfg


def fetch_gene_version(
    species: str,
    config: Optional[dict] = None
) -> str:
    """
    Get the version of the Gesel gene annotation file specification used by the species of interest.

    Args:
        species:
            Taxonomy ID of the species of interest.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        Version of the gene annotation file specificion used by ``species``.

    Examples:
        >>> import gesel
        >>> gesel.fetch_gene_version("9606")
    """

    config = cfg._get_config(config)
    cached = cfg._get_cache(config, "fetch_gene_version", species)
    if cached is not None:
        return cached

    version = None
    try:
        payload = cfg._fetch_gene(config, species + "_gene-version.tsv")
    except:
        version = "0.1.0"

    if version is None:
        with open(payload, "r") as handle:
            version = handle.readline().strip()
    
    cfg._set_cache(config, "fetch_gene_version", species, version)
    return version
