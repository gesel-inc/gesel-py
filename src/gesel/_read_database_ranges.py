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
            List of integers containing the zero-indexed closed start of each byte range to extract from the file.
            This list may be empty.

        end:
            List of integers containing the zero-indexed open end of each byte range to extract from the file.
            This should have the same length as ``start`` such that the ``i``-th range is defined as ``[start[i], end[i])``.
            All ranges supplied in a single call to this function should be non-overlapping.

    Returns:
        List of byte strings containing the requested bytes for each range.
        For ranges where ``end <= start``, an empty string is returned.

    Examples:
        >>> import tempfile
        >>> tmp = tempfile.mkdtemp()
        >>> import os
        >>> dpath = os.path.join(tmp, "foo.txt")
        >>> with open(dpath, "wb") as handle:
        ...     handle.write(b"abcdefghijklmnopqrstuvwxyz\n")
        >>>
        >>> import gesel
        >>> gesel.read_database_ranges(tmp, "foo.txt", [0, 20, 10, 5], [6, 23, 15, 14])
    """

    ordering = biocutils.order(start)
    output = [b''] * len(start)
    with open(os.path.join(path, name), "rb") as handle:
        for o in ordering:
            s = start[o]
            e = end[o]
            if s < e:
                handle.seek(s)
                output[o] = handle.read(e - s)
    return output
