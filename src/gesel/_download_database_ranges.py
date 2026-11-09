from ._download_database_file import database_url
from . import _utils as utils
from typing import Optional
import requests


def download_database_ranges(
    name: str,
    start: list[int],
    end: list[int],
    url: Optional[str] = None,
    multipart: bool = False,
    concurrency: Optional[int] = None 
) -> list[str]:
    """
    Download any number of byte ranges from a Gesel database file.

    Args:
        name:
            Name of the file.
            This usually has the species identifier as a prefix.

        start:
            List of integers containing the start of each byte range,
            see the ``start`` argument to be passed to the ``fetch_ranges`` function in :py:func:`~gesel.new_config`.

        end:
            List of integers containing the end of each byte range,
            see the ``end`` argument to be passed to the ``fetch_ranges`` function in :py:func:`~gesel.new_config`.

        url:
            Base URL to the Gesel database files.
            If ``None``, it is set to :py:func:`~gesel.database_url`.

        multipart:
            Whether the server at ``url`` supports multi-part range requests.

        concurrency:
            Maximum number of concurrent range requests.
            If ``None``, defaults to :py:func:`~gesel.range_concurrency`.
            Only used if ``multipart = False``.

    Returns:
        List of tuples containing the retrieved byte ranges,
        see the return value of the ``fetch_ranges`` function in :py:func:`~gesel.new_config`.

    Examples:
        >>> import gesel
        >>> gesel.download_database_ranges("9606_set2gene.tsv", [0], [100])
        >>> gesel.download_database_ranges("9606_set2gene.tsv", [10, 100, 1000], [20, 150, 1100])
    """

    if url is None:
        url = database_url()
    url = url + "/" + name

    if multipart:
        return download_multipart_ranges(url, start, end)

    if concurrency is None:
        concurrency = range_concurrency()
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers = concurrency) as executor:
        collected = []
        for i in range(len(start)):
            collected.append(executor.submit(_make_range_request, url, start[i], end[i]))
        output = []
        for val in collected:
            output.append(val.result())

    return output


_range_concurrency = 10


def range_concurrency(concurrency: Optional[int] = None):
    """
    Set the default number of threads for concurrent range requests in :py:func:`~gesel.download_database_ranges`.

    Args:
        concurrency:
            Number of threads.

    Results:
        If ``concurrency = None``, the number of threads is returned (default 10).

        If ``concurrency`` is provided, it is used to set the number of threads, and the previous number of threads is returned.

    Examples:
        >>> import gesel
        >>> gesel.range_concurrency()
        >>> old = gesel.range_concurrency(5)
        >>> print(old)
        >>> gesel.range_concurrency(old)
    """
    global _range_concurrency
    previous = _range_concurrency
    if concurrency is not None:
        _range_concurrency = concurrency
    return previous


def _make_range_request(url, curstart, curend) -> tuple:
    resp = requests.get(url, headers = { "Range": "bytes=" + str(curstart) + "-" + str(curend - 1) }) # byte ranges are closed intervals, not half-open.
    if resp.status_code >= 300:
        raise utils._format_error(resp)
    if resp.status_code != 206:
        raise ValueError("expected a partial content response from a range request")
    loc_start, loc_end = _extract_range_location(resp.headers["Content-Range"].encode("UTF-8"))
    # We use 'content' instead of 'text' to handle multi-byte characters correctly.
    return resp.content, loc_start, loc_end 


def _extract_range_location(crange) -> tuple:
    to_bytes = crange.find(b"bytes ")
    to_dash = crange.find(b"-")
    to_slash = crange.find(b"/")
    if to_bytes == -1 or to_dash == -1 or to_slash == -1 or to_dash >= to_slash:
        raise RuntimeError("expected 'content-range' header to follow a 'bytes <start>-<end>/<size>' format")
    curstart = int(crange[(to_bytes + 6):to_dash])
    curend = int(crange[(to_dash + 1):to_slash]) + 1 # convert to an open end for consistency.
    return curstart, curend


def download_multipart_ranges(
    url: str,
    start: list[int],
    end: list[int],
    _mock = None
) -> list[str]:
    """
    Perform a multi-part range request on a Gesel database file.

    Args:
        url:
            URL to a specific Gesel database file.

        start:
            List of integers containing the start of each byte range,
            see the ``start`` argument to be passed to the ``fetch_ranges`` function in :py:func:`~gesel.new_config`.

        end:
            List of integers containing the end of each byte range,
            see the ``end`` argument to be passed to the ``fetch_ranges`` function in :py:func:`~gesel.new_config`.

        _mock:
            Internal use only.

    Returns:
        List of tuples containing the retrieved byte ranges,
        see the return value of the ``fetch_ranges`` function in :py:func:`~gesel.new_config`.

    Examples:
        >>> import gesel
        >>> url = gesel.database_url() + "/9606_set2gene.tsv" 
        >>> gesel.download_multipart_ranges(url, [0], [100])
        >>> # Note: as of writing, GitHub releases don't support multi-part range requests.
    """

    if len(start) == 0:
        return []
    if len(start) == 1:
        return [_make_range_request(url, start[0], end[0])]

    formatted = []
    for curstart, curend in zip(start, end):
        formatted.append(str(curstart) + "-" + str(curend - 1)) # byte ranges are closed intervals, not half-open.
    if _mock is None:
        resp = requests.get(url, headers = { "Range": "bytes=" + ", ".join(formatted) })
    else:
        resp = _mock(url, "bytes=" + ", ".join(formatted)) 
    if resp.status_code >= 300:
        raise utils._format_error(resp)
    if resp.status_code != 206:
        raise ValueError("expected a partial content response from a range request")

    ct = resp.headers["Content-Type"]
    prefix = "multipart/byteranges; boundary="
    if not ct.startswith(prefix):
        raise RuntimeError("unexpected content type from multi-part range request")
    boundary = ct[len(prefix):]

    # Remember, we operate on the byte strings to correctly handle ranges for multi-byte characters.
    return _parse_multipart_response(resp.content, boundary.encode("utf-8"))


# WARNING: this part only works when the contents of body are fully string-able;
# otherwise, if it's binary data, we really should be working with them as raw data.
def _parse_multipart_response(body: bytes, boundary: bytes) -> tuple[list, list]:
    position = 0
    boundary = b"--" + boundary
    contents = []

    while True:
        if body[position:(position + len(boundary))] != boundary:
            raise RuntimeError("missing boundary in multi-part range request")
        position += len(boundary)

        remaining = body[position:(position + 2)]
        if remaining == b"--":
            break 
        if remaining != b"\r\n":
            raise RuntimeError("unexpected content range format in multi-part response")
        position += 2

        # Running through all headers. 
        headers = {}
        while True:
            crlf = body.find(b"\r\n", position)
            if crlf == -1:
                raise RuntimeError("failed to find CRLF to terminate headers in multi-part response")
            curline = body[position:crlf]
            position = crlf + 2
            if curline == b"": # headers terminate at a CRLF empty line.
                break 
            at_colon = curline.find(b":")
            headers[curline[:at_colon].lower()] = curline[(at_colon+1):]

        if b"content-range" not in headers:
            raise RuntimeError("expected a 'content-range' header in each multi-part response")
        first, last = _extract_range_location(headers[b"content-range"])
        endpos = position + last - first
        contents.append((body[position:endpos], first, last))
        position = endpos

        remaining = body[position:(position + 2)]
        if remaining != b"\r\n":
            raise RuntimeError("expected a newline after each part of a multi-part response")
        position += 2

    return contents
