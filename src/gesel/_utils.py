from typing import Optional
import os
import urllib.parse
import requests
import datetime


def _format_error(res):
    ctype = res.headers["content-type"]
    if ctype == "text/plain":
        return requests.HTTPError(res.status_code, res.text)
    else:
        return requests.HTTPError(res.status_code)


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


def _download_file(
    cache: Optional[str],
    url: str,
    overwrite: bool
) -> str:
    if cache is None:
        cache = cache_directory()

    os.makedirs(cache, exist_ok=True)
    name = urllib.parse.quote_plus(url)
    target = os.path.join(cache, name)

    if overwrite or not os.path.exists(target):
        # Saving to a temporary file and renaming it on success,
        # so we don't fail with a partially downloaded file in the cache.
        import tempfile
        tempfid, temppath = tempfile.mkstemp(dir=cache)
        os.close(tempfid) # avoid opening a handle to this file until we need it.

        try:
            import shutil
            with requests.get(url, stream=True) as r:
                if r.status_code >= 300:
                    raise _format_error(r)
                with open(temppath, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
            shutil.move(temppath, target) # this should be more or less atomic when both paths are on the same filesystem, so we'll omit the locks.
        finally:
            if os.path.exists(temppath):
                os.remove(temppath)

    return target


def _decode_indices(line: str) -> list:
    if line == b"\n":
        return []

    details = line.rstrip().split(b"\t") 
    last = 0
    for i, x in enumerate(details):
        last += int(x)
        details[i] = last
    return details 
