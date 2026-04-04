from typing import Optional
import biocframe
from . import _utils as utils
from . import _new_config as cfg 


def fetch_all_collections(species: str, config: Optional[dict] = None) -> biocframe.BiocFrame:
    """
    Fetch information about all gene set collections in the Gesel database.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        A :py:class:`~biocframe.BiocFrame` where each row represents a collection.
        This contains the following columns:

        - ``title``, string containing the title of the collection.
        - ``description``, string containing a description of the collection.
        - ``maintainer``, string containing the identity of the collection's maintainer.
        - ``source``, string containing the source of origin of the collection.
        - ``start``, integer containing the set index of the first gene set in this collection.
          The set index refers to a row in the data frame returned by :py:func:`~gesel.fetch_all_sets`.
        - ``size``, integer specifying the number of gene sets in the collection.

        If this function is called once, the data frame will be cached in memory and re-used in subsequent calls.
        The cached information will also be used to speed up :py:func:`~gesel.fetch_some_collections`.

    Examples:
        >>> import gesel
        >>> df = gesel.fetch_all_collections("9606")
        >>> print(df)
    """

    config = cfg.get_config(config)
    candidate = cfg.get_cache(config, "fetch_all_collections", species)
    if candidate is not None:
        return candidate

    fname = species + "_collections.tsv.gz"
    path = cfg.fetch_file(config, fname)

    title = []
    desc = []
    maintainer = []
    src = []
    start = []
    size = []
    last = 0

    import gzip
    with gzip.open(path, "rb") as f:
        for line in f:
            details = line.decode("utf-8").split("\t")
            title.append(details[0])
            desc.append(details[1])
            maintainer.append(details[3])
            src.append(details[4])
            start.append(last)
            cursize = int(details[5])
            size.append(cursize)
            last += cursize

    output = biocframe.BiocFrame({
        "title": title,
        "description": desc,
        "maintainer": maintainer,
        "source": src,
        "start": start,
        "size": size
    })

    cfg.set_cache(config, "fetch_all_collections", species, output)
    return output
