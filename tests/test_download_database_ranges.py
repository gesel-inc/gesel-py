import gesel
import tempfile
import os
import gesel._utils as ut
from gesel._download_database_ranges import _parse_multipart_response


tmpdir = None


def get_full_contents(name):
    global tmpdir
    if tmpdir is None:
        tmpdir = tempfile.mkdtemp()
    out = gesel.download_database_file(name, cache=tmpdir)
    with open(out, "rb") as f:
        return f.read()


def test_download_database_ranges_no_multipart():
    full_contents = get_full_contents("9606_collections.tsv")

    starts = [0, 10, 20]
    ends = [5, 17, 27]
    ranges = gesel.download_database_ranges("9606_collections.tsv", starts, ends)
    assert len(ranges) == len(starts)
    for i, currange in enumerate(ranges):
        assert starts[i] >= currange[1]
        assert ends[i] <= currange[2]
        assert currange[0] == full_contents[currange[1]:currange[2]]

    empty = gesel.download_database_ranges("9606_collections.tsv", [], [])
    assert len(empty) == 0


def test_range_concurrency():
    assert gesel.range_concurrency() > 0
    old = gesel.range_concurrency(5)
    assert gesel.range_concurrency() == 5
    gesel.range_concurrency(old)
    assert gesel.range_concurrency() == old


class MockRequest:
    def __init__(self, status_code, content, headers):
        self.status_code = status_code
        self.content = content
        self.headers = headers


def mock_request(url, ranges):
    global tmpdir
    if tmpdir is None:
        tmpdir = tempfile.mkdtemp()

    out = ut._download_file(url=url, cache=tmpdir, overwrite=False)
    with open(out, "rb") as f:
        full_contents = f.read()

    if not ranges.startswith("bytes="):
        raise ValueError("oops") 
    ranges = ranges[6:].split(", ")

    import random
    if len(ranges) == 1:
        x = ranges[0]
        equals = x.find("-")

        # Adding some jitter.
        start = max(0, int(x[:equals]) - random.randint(0, 10))
        end = min(len(full_contents), int(x[equals + 1:]) + 1 + random.randint(0, 10))

        return MockRequest(206, full_contents[start:end], { "Content-Range": "bytes " + str(start) + "-" + str(end - 1) + "/" + str(len(full_contents)) })

    output = b""
    boundary = b"FOOBAR"
    for x in ranges:
        equals = x.find("-")

        # Adding some jitter.
        start = max(0, int(x[:equals]) - random.randint(0, 10))
        end = min(len(full_contents), int(x[equals + 1:]) + 1 + random.randint(0, 10))

        output += b"--" + boundary + b"\r\nContent-Range: bytes "
        output += str(start).encode("utf-8") + b"-" + str(end - 1).encode("utf-8") + b"/" + str(len(full_contents)).encode("utf-8")
        output += b"\r\n\r\n" + full_contents[start:end] + b"\r\n"
    output += b"--" + boundary + b"--"

    return MockRequest(206, output, { "Content-Type": "multipart/byteranges; boundary=" + boundary.decode("UTF-8") })


def test_download_multipart_ranges():
    full_contents = get_full_contents("9606_collections.tsv")
    url = gesel.database_url() + "/9606_collections.tsv"

    # A simple request to start things off.
    starts = [0, 10, 20]
    ends = [5, 17, 27]
    ranges = gesel.download_multipart_ranges(url, starts, ends, _mock=mock_request)
    assert len(ranges) == len(starts) # our mock implementation doesn't merge or reorder.
    for i, currange in enumerate(ranges):
        assert starts[i] >= currange[1]
        assert ends[i] <= currange[2]
        assert currange[0] == full_contents[currange[1]:currange[2]]

    # Behaves with just a single range.
    single = gesel.download_multipart_ranges(url, [13], [39], _mock=mock_request)
    assert len(single) == 1
    assert 13 >= single[0][1]
    assert 39 <= single[0][2]
    assert single[0][0] == full_contents[single[0][1]:single[0][2]]

    # Or even no ranges.
    empty = gesel.download_multipart_ranges(url, [], [], _mock=mock_request)
    assert len(empty) == 0


def test_parse_multipart_ranges():
    payload1 = "asdasd🙃🙃🙃asd".encode("utf-8")
    payload2 = b"hottle\r\nwhee\nblah\r\n"
    payload3 = b"Content-Type: asdasd\r\nContent-Range: 942835723948"

    ex = b"\r\n".join([
        b"--foo", 
        b"Content-Range: bytes 10-" + str(10 + len(payload1) - 1).encode("utf-8") + b"/100",
        b"Content-Type: text/plain",
        b"",
        payload1,
        b"--foo",
        b"Content-Range: bytes 30-" + str(30 + len(payload2) - 1).encode("utf-8") + b"/100", # different ordering of headers
        b"Content-Type: text/plain",
        b"",
        payload2,
        b"--foo",
        b"Content-Range: bytes 50-" + str(50 + len(payload3) - 1).encode("utf-8") + b"/100", # different ordering of headers
        b"Content-Type: text/plain",
        b"",
        payload3,
        b"--foo--"
    ])

    contents = _parse_multipart_response(ex, b"foo") 
    assert [x[0] for x in contents] == [payload1, payload2, payload3]
    assert [x[1] for x in contents] == [10, 30, 50]
    for x in contents:
        assert x[2] == x[1] + len(x[0])
