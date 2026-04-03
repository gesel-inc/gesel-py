from . import _new_config as cfg
from typing import Optional
import biocframe


def fetch_all_genes(
    species: str,
    types: list = ["symbol", "entrez", "ensembl"],
    config: Optional[dict] = None
) -> biocframe.BiocFrame:
    """
    Fetch names and identifiers of various types for all genes.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        types:
            Types of gene names to return.
            Typically one or more of ``symbol``, ``entrez``, and/or ``ensembl``.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        Data frame where each row represents a gene.
        Each column corresponds to one of the ``types`` and is a list of lists.
        Each inner list in the column contains the names of the specified type for each gene.

    Examples:
        >>> import gesel
        >>> df = gesel.fetch_all_genes("9606")
        >>> print(df)
        >>> print(df["symbol"][1:10])
    """

    config = cfg.get_config(config)
    cached = cfg.get_cache(config, "fetch_all_genes", species)

    modified = False
    if cached is None:
        cached = {}

    output = {}
    for t in types:
        if t in cached:
            output[t] = cached[t]
            continue

        path = cfg.fetch_gene(config, species + "_" + t + ".tsv.gz")
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
        cfg.set_cache(config, "fetch_all_genes", species, cached)

    return biocframe.BiocFrame(output)
