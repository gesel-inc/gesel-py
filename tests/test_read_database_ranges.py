import tempfile
import gesel
import os


def test_read_database_ranges():
    tmp = tempfile.mkdtemp()
    dpath = os.path.join(tmp, "foo.txt")
    contents = b"abcdefghijklmnopqrstuvwxyz\n"
    with open(dpath, "wb") as handle:
        handle.write(contents)

    starts = [0, 5, 10, 20]
    ends = [4, 6, 15, 24]
    observed = gesel.read_database_ranges(tmp, "foo.txt", starts, ends)
    for i in range(len(starts)):
        s = starts[i]
        e = ends[i]
        assert contents[s:e] == observed[i][0]
        assert s == observed[i][1]
        assert e == observed[i][2]
