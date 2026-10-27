from typing import Optional
import biocframe

from . import _new_config as cfg
from ._fetch_gene_types import fetch_gene_types
from ._fetch_gene_version import fetch_gene_version


def fetch_all_genes(
    species: str,
    types: Optional[list] = None,
    config: Optional[dict] = None
) -> biocframe.BiocFrame:
    """
    Fetch identifiers for all genes.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        types:
            Types of gene identifiers to return.
            If ``None``, this is taken from :py:func:`~gesel.fetch_gene_types`.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        A :py:class:`~biocframe.BiocFrame` where each row represents a gene.
        Each column corresponds to one of the ``types`` and is a list of lists.
        Each inner list in the column contains the identifiers of the specified type for each gene.

    Examples:
        >>> import gesel
        >>> df = gesel.fetch_all_genes("9606")
        >>> print(df)
        >>> print(df["symbol"][1:10])
    """

    config = cfg._get_config(config)
    cached = cfg._get_cache(config, "fetch_all_genes", species)

    modified = False
    if cached is None:
        cached = {}

    if types is None:
        types = fetch_gene_types(species, config)
    if fetch_gene_version(species, config) == "0.1.0":
        sep = "_"
    else:
        sep = "_gene-type-"

    output = {}
    for t in types:
        if t in cached:
            output[t] = cached[t]
            continue

        path = cfg._fetch_gene(config, species + sep + t + ".tsv.gz")
        collected = []

        import gzip
        with gzip.open(path, "rb") as f:
            for line in f:
                line = line.rstrip()
                if line == b"":
                    collected.append([])
                else:
                    collected.append(line.decode("utf-8").split("\t"))

        output[t] = collected
        cached[t] = collected
        modified = True

    if modified:
        cfg._set_cache(config, "fetch_all_genes", species, cached)

    return biocframe.BiocFrame(output)
