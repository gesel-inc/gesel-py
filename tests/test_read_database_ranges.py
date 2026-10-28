import tempfile
import gesel
import os


def test_read_database_ranges():
    tmp = tempfile.mkdtemp()
    dpath = os.path.join(tmp, "foo.txt")
    contents = b"abcdefghijklmnopqrstuvwxyz\n"
    with open(dpath, "wb") as handle:
        handle.write(contents)

    # Handles out-of-order starts.
    starts = [0, 20, 10, 5]
    ends = [6, 23, 15, 14]
    observed = gesel.read_database_ranges(tmp, "foo.txt", starts, ends)
    for i in range(len(starts)):
        s = starts[i]
        e = ends[i]
        assert contents[s:e] == observed[i]

    # Handles empty or preceding ends.
    starts = [2, 20, 10, 5]
    ends = [6, 19, 15, 5]
    observed = gesel.read_database_ranges(tmp, "foo.txt", starts, ends)
    for i in range(len(starts)):
        s = starts[i]
        e = ends[i]
        if s < e:
            assert contents[s:e] == observed[i]
        else:
            assert observed[i] == b""
