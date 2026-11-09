import os
import biocutils 


def read_database_ranges(path: str, name: str, start: list, end: list) -> list:
    """
    Read any number of byte ranges from a Gesel database file on the local filesystem.

    Args:
        path:
            Path to the directory containing the Gesel database file on disk.

        name:
            Name of the file.
            This usually has the species identifier as a prefix.

        start:
            List of integers containing the start of each byte range,
            see the ``start`` argument to be passed to the ``fetch_ranges`` function in :py:func:`~gesel.new_config`.

        end:
            List of integers containing the end of each byte range,
            see the ``end`` argument to be passed to the ``fetch_ranges`` function in :py:func:`~gesel.new_config`.

    Returns:
        List of tuples containing the retrieved byte ranges,
        see the return value of the ``fetch_ranges`` function in :py:func:`~gesel.new_config`.

    Examples:
        >>> import tempfile
        >>> tmp = tempfile.mkdtemp()
        >>> import os
        >>> dpath = os.path.join(tmp, "foo.txt")
        >>> with open(dpath, "wb") as handle:
        ...     handle.write(b"abcdefghijklmnopqrstuvwxyz\\n")
        >>>
        >>> import gesel
        >>> gesel.read_database_ranges(tmp, "foo.txt", [0, 20, 10, 5], [6, 23, 15, 14])
    """

    output = []
    with open(os.path.join(path, name), "rb") as handle:
        for s, e in zip(start, end):
            handle.seek(s)
            output.append((handle.read(e - s), s, e))
    return output
