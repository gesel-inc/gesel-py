from typing import Optional, Callable, Any
from ._download_database_file import download_database_file
from ._download_gene_file import download_gene_file
from ._download_database_ranges import download_database_ranges


def new_config(
    fetch_gene: Optional[Callable] = None,
    fetch_gene_kwargs: dict = {},
    fetch_file: Optional[Callable] = None,
    fetch_file_kwargs: dict = {},
    fetch_ranges: Optional[Callable] = None,
    fetch_ranges_kwargs: dict = {},
    consolidate_block_size: Optional[int] = None
) -> dict:
    """
    Create a new configuration object to specify how the Gesel database should be queried.
    This can be passed to each Gesel function to alter its behavior in a consistent manner.
    For example, we could point to a different Gesel database from the default,
    or we can override ``fetch_file`` to retrieve database files from a shared filesystem instead of performing a HTTP request.

    The configuration list also contains a cache of data structures that can be populated by Gesel functions.
    This avoids unnecessary fetch requests upon repeated calls to the same function.
    If the cache becomes stale or too large, it can be cleared by calling :py:func:`~flush_memory_cache`.

    If no configuration list is supplied to Gesel functions, the default configuration is used.
    The default is created by calling ``new_config()`` without any arguments.

    Args:
        fetch_gene:
            Function that accepts the name of the file in the Gesel gene descriptions and returns an absolute path to the file.
            If ``None``, it defaults to :py:func:`~gesel.download_gene_file`.

        fetch_gene_kwargs:
            Dictionary of name:value pairs containing extra arguments to pass to ``fetch_gene``.

        fetch_file: 
            Function that accepts the name of the file in the Gesel database and returns an absolute path to the file.
            If ``None``, it defaults to :py:func:`~gesel.download_database_file`.

        fetch_file_kwargs:
            Dictionary of name:value pairs containing extra arguments to pass to ``fetch_file``.

        fetch_ranges:
            Function that accepts three arguments:

            - ``name``, the name of a Gesel database file.
            - ``start``, a list of integers containing the zero-indexed closed start of each byte range to extract from the file.
              This may be of zero length.
            - ``end``, a list of integers containing the zero-indexed open end of each byte range to extract from the file.
              This should have the same length as ``start`` such that the ``i``-th byte range is defined as ``[start[i], end[i])``.
              The set of byte ranges should be non-empty, non-overlapping, and sorted by increasing start/end position.

            It should return a list containing tuples of:

            1. A byte string representing the contents of a "retrieved" byte range.
            2. An integer containing the zero-indexed closed start of the retrieved range.
            3. An integer containing the zero-indexed open end of the retrieved range.

            All retrieved byte ranges are non-empty but may be overlapping and in any order.
            Each "requested" byte range (i.e., defined by ``start`` and ``end``) will be enclosed within at least one retrieved byte range.
            Note that the retrieved byte ranges may not have a 1-to-1 mapping to the requested byte ranges,
            e.g., if the server decides that adjacent requested ranges can be merged into a single output range.

            If ``None``, it defaults to :py:func:`~gesel.download_database_ranges`.

        fetch_ranges_kwargs:
            Dictionary of name:value pairs containing extra arguments to pass to ``fetch_ranges``.

        consolidate_block_size:
            Block size for consolidated requests.
            If ``None``, it defaults to :py:func:`~gesel.consolidate_block_size`.

    Returns:
        Dictionary of Gesel configuration settings.

    Examples:
        >>> import gesel
        >>> gesel.new_config()
    """

    return {
        "cache": {},
        "fetch_gene": fetch_gene,
        "fetch_gene_kwargs": fetch_gene_kwargs,
        "fetch_file": fetch_file,
        "fetch_file_kwargs": fetch_file_kwargs,
        "fetch_ranges": fetch_ranges,
        "fetch_ranges_kwargs": fetch_ranges_kwargs,
        "consolidate_block_size": consolidate_block_size
    }


_default_config = None


def _get_config(config: Optional[dict]) -> dict:
    if config is None:
        global _default_config
        config = _default_config
        if config is None:
            _default_config = new_config()
            config = _default_config
    return config


def _fetch_gene(config: dict, *args, **kwargs) -> str:
    fetch_gene = config["fetch_gene"]
    if fetch_gene is None:
        fetch_gene = download_gene_file
    return fetch_gene(*args, **kwargs, **(config["fetch_gene_kwargs"]))


def _fetch_file(config: dict, *args, **kwargs) -> str:
    fetch_file = config["fetch_file"]
    if fetch_file is None:
        fetch_file = download_database_file
    return fetch_file(*args, **kwargs, **(config["fetch_file_kwargs"]))


def _fetch_ranges(config: dict, *args, **kwargs) -> list[bytes]:
    fetch_ranges = config["fetch_ranges"]
    if fetch_ranges is None:
        fetch_ranges = download_database_ranges
    return fetch_ranges(*args, **kwargs, **(config["fetch_ranges_kwargs"]))


def flush_memory_cache(config: Optional[dict] = None):
    """
    Flush the in-memory cache for Gesel data structures in the current Python session.
    By default, Gesel functions caches the data structures in the current session to avoid unnecessary requests to the filesystem and remote server.
    On rare occasion, these cached data structures may be out of date when the Gesel database files change.
    In such cases, the cache can be flushed to ensure that the various Gesel functions operate on the latest version of the database.

    Args:
        config:
            Configuration object created by :py:func:`~new_config`.
            If ``None``, the default configuration is used.

    Returns:
        The in-memory cache in ``config`` is cleared.

    Examples:
        >>> import gesel
        >>> gesel.flush_memory_cache()
    """
    config = _get_config(config)
    config["cache"] = {}


def _get_cache(config: dict, context: str, species: str) -> Optional[Any]:
    cache = config["cache"]
    if context in cache:
        available = cache[context]
        if species in available:
            return available[species]
    return None


def _set_cache(config: dict, context: str, species: str, value: Any):
    cache = config["cache"]
    if context not in cache:
        cache[context] = {}
    cache[context][species] = value


def _retrieve_ranges(config: dict, name: str) -> list:
    path = _fetch_file(config, name + ".ranges.gz")
    import gzip
    with gzip.open(path, "r") as f:
        boundaries = [0]
        last = 0
        for line in f:
            last += int(line) + 1 # +1 for the newline
            boundaries.append(last)
        return boundaries


def _retrieve_ranges_with_sizes(config: dict, name: str) -> tuple:
    path = _fetch_file(config, name + ".ranges.gz")
    import gzip
    with gzip.open(path, "r") as f:
        boundaries = [0]
        last = 0
        sizes = []
        for line in f:
            details = line.split(b"\t")
            last += int(details[0]) + 1 # +1 for the newline
            boundaries.append(last)
            sizes.append(int(details[1]))
        return boundaries, sizes


def _retrieve_ranges_with_names(config: dict, name: str) -> tuple:
    path = _fetch_file(config, name + ".ranges.gz")
    import gzip
    with gzip.open(path, "r") as f:
        boundaries = [0]
        last = 0
        names = []
        for line in f:
            details = line.split(b"\t")
            names.append(details[0])
            last += int(details[1]) + 1 # +1 for the newline
            boundaries.append(last)
        return names, boundaries
