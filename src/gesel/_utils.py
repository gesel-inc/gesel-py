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


def _download_file(
    cache: Optional[str],
    url: str,
    overwrite: bool
) -> str:
    if cache is None:
        import appdirs
        cache = appdirs.user_cache_dir("gesel")

    os.makedirs(cache, exist_ok=True)
    name = urllib.parse.quote_plus(url)
    target = os.path.join(cache, name)

    if overwrite or not os.path.exists(target):
        # Saving to a temporary file and renaming it on success,
        # so we don't fail with a partially downloaded file in the cache.
        import tempfile
        _, temppath = tempfile.mkstemp(dir=cache)

        try:
            with requests.get(url, stream=True) as r:
                if r.status_code >= 300:
                    raise _format_error(r)
                import shutil
                with open(temppath, "wb") as f:
                    shutil.copyfileobj(r.raw, f)
            os.rename(temppath, target) # this should be more or less atomic, so no need for locks.
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
