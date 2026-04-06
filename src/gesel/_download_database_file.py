from typing import Optional
from . import _utils as utils


def download_database_file(
    name: str,
    url: Optional[str] = None,
    cache: Optional[str] = None,
    overwrite: bool = False
) -> str:
    """
    Download Gesel database files and store them in a cache on the local file system.

    Args:
        name:
            Name of the file.
            This usually has the species identifier as a prefix.

        url:
            Base URL to the Gesel database files.
            If ``None``, it is set to :py:func:`~database_url`.

        cache:
            Path to a cache directory.
            If ``None``, it is set to :py:func:`~cache_directory`.

        overwrite:
            Boolean indicating whether any cached file should be overwritten with a new download.

    Returns:
        Path to the downloaded file on the local file system.

    Examples:
        >>> import gesel
        >>> gesel.download_database_file("9606_collections.tsv.gz")
    """
    if url is None:
        url = database_url()
    return utils._download_file(cache, url + "/" + name, overwrite)


_db_url = None


def database_url(url: Optional[str] = None) -> str:
    """
    Get or set the base URL to the Gesel database files, which is used in :py:func:`~download_database_file`.

    Args:
        url: 
            The new database URL.

    Returns:
        If ``url = None``, the URL to the Gesel database is returned.
        The URL defaults to the `GitHub releases page <https://github.com/LTLA/gesel-feedstock>`_;
        this can be altered by setting the ``GESEL_DATABASE_URL`` environment variable before the first call to this function.

        If ``url`` is provided, this function sets the database URL to ``url``, and returns the previous value of the URL.

    Examples:
        >>> import gesel
        >>> gesel.database_url()
        >>> old = gesel.database_url("https://foo.bar")
        >>> gesel.database_url(old)
        >>> gesel.database_url()
    """

    global _db_url
    if _db_url is None:
        import os
        if "GESEL_DATABASE_URL" in os.environ:
            _db_url = os.environ["GESEL_DATABASE_URL"]
        else:
            _db_url = "https://github.com/LTLA/gesel-feedstock/releases/download/indices-v0.2.1"

    previous = _db_url
    if url is not None:
        _db_url = url
    return previous
