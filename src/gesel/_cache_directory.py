from typing import Optional
import os


_cache_directory = None


def cache_directory(path: Optional[str] = None) -> str:
    """
    Get or set the default cache directory for :py:func:`~gesel.download_database_file` and :py:func:`~gesel.download_gene_file`.

    Args:
        path:
            Path to a new cache directory.

    Returns:
        If ``path = None``, the path to the Gesel cache directory is returned.
        This defaults to a location defined by the **appdirs** package,
        and can be changed by setting the ``GESEL_CACHE_DIRECTORY`` environment variable before the first call to this function.

        If ``path`` is provided, it is used to set the location of the cache directory, and the previous location is returned.

    Examples:
        >>> import gesel
        >>> gesel.cache_directory()
        >>> old = gesel.cache_directory("/tmp/foo/bar") # setting it.
        >>> gesel.cache_directory() # now it's changed.
        >>> gesel.cache_directory(old) # setting it back.
    """
    global _cache_directory
    if _cache_directory is None:
        if "GESEL_CACHE_DIRECTORY" in os.environ:
            _cache_directory = os.environ["GESEL_CACHE_DIRECTORY"]
        else:
            import appdirs
            _cache_directory = appdirs.user_cache_dir("gesel")

    previous = _cache_directory
    if path is not None:
        _cache_directory = path
    return previous
