from typing import Optional
from . import _new_config as cfg
from ._fetch_all_collections import fetch_all_collections
import biocframe


def fetch_all_sets(species: str, config: Optional[dict] = None) -> biocframe.BiocFrame:
    """
    Fetch information about all gene sets in the Gesel database.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``NULL``, the default configuration is used.

    Returns:
        A :py:class:`~biocframe.BiocFrame` where each row represents a gene set.
        This contains the following columns:

        - ``name``, string containing the name of the gene set.
        - ``description``, string containing a description of the gene set.
        - ``size``: integer specifying the number of genes in this gene set.
        - ``collection``: integer, the collection index of the collection that contains this gene set.
           The collection index refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_collections`.
        - ``number``: integer, the position of the gene set inside the specified collection.
          The set index of the current gene set is defined by adding ``number` to the collection's ``start``. 

        If this function is called once, the data frame will be cached in memory and re-used in subsequent calls.
        The cached information will also be used to speed up :py:func:`~gesel.fetch_some_sets`.

    Examples:
        >>> import gesel
        >>> df = gesel.fetch_all_sets("9606")
        >>> print(df)
    """

    config = cfg.get_config(config)
    candidate = cfg.get_cache(config, "fetch_all_sets", species)
    if candidate is not None:
        return candidate

    fname = species + "_sets.tsv.gz"
    path = cfg.fetch_file(config, fname)

    name = []
    desc = []
    size = []

    import gzip
    with gzip.open(path, "rb") as f:
        for line in f:
            details = line.rstrip().decode("utf-8").split("\t")
            name.append(details[0])
            desc.append(details[1])
            size.append(int(details[2]))

    info = fetch_all_collections(species, config=config)
    collection = []
    number = []
    for cidx in range(info.shape[0]):
        csize = info["size"][cidx]
        collection += [cidx] * csize
        number += list(range(csize))

    output = biocframe.BiocFrame({
        "name": name,
        "description": desc,
        "size": size,
        "collection": collection,
        "number": number
    })

    cfg.set_cache(config, "fetch_all_sets", species, output)
    return output
