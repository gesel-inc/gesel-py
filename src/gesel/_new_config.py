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
    fetch_ranges_kwargs: dict = {}
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
            Function that accepts three arguments - 
            the name of the file in the Gesel database, an integer vector containing the starts of the byte ranges, and another vector containing the ends of the byte ranges -
            and returns a list of byte strings containing the contents of the specified ranges.
            If ``None``, it defaults to :py:func:`~gesel.download_database_ranges`.

        fetch_ranges_kwargs:
            Dictionary of name:value pairs containing extra arguments to pass to ``fetch_ranges``.

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
        "fetch_ranges_kwargs": fetch_ranges_kwargs
    }


default_config = None


def get_config(config: Optional[dict]) -> dict:
    if config is None:
        global default_config
        config = default_config
        if config is None:
            default_config = new_config()
            config = default_config
    return config


def fetch_gene(config: dict, *args, **kwargs) -> str:
    fetch_gene = config["fetch_gene"]
    if fetch_gene is None:
        fetch_gene = download_gene_file
    return fetch_gene(*args, **kwargs, **(config["fetch_gene_kwargs"]))


def fetch_file(config: dict, *args, **kwargs) -> str:
    fetch_file = config["fetch_file"]
    if fetch_file is None:
        fetch_file = download_database_file
    return fetch_file(*args, **kwargs, **(config["fetch_file_kwargs"]))


def fetch_ranges(config: dict, *args, **kwargs) -> list[bytes]:
    fetch_ranges <- config["fetch_ranges"]
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
    config = get_config(config)
    config["cache"] = {}


def get_cache(config: dict, context: str, species: str) -> Optional[Any]:
    cache = config["cache"]
    if context in cache:
        available = cache[context]
        if species in available:
            return available[species]
    return None


def set_cache(config: dict, context: str, species: str, value: Any):
    cache = config["cache"]
    if context not in cache:
        cache[context] = {}
    cache[context][species] = value
