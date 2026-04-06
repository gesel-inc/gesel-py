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


def test_download_database_ranges():
    full_contents = get_full_contents("9606_collections.tsv")

    starts = [0, 10, 20]
    ends = [5, 17, 27]
    ranges = gesel.download_database_ranges("9606_collections.tsv", starts, ends)
    for i in range(len(starts)):
        assert ranges[i] == full_contents[starts[i]:ends[i]]

    # Skips invalid ranges.
    starts = [0, 10, 20, 30]
    ends = [0, 15, 18, 40]
    ranges = gesel.download_database_ranges("9606_collections.tsv", starts, ends)
    for i in range(len(starts)):
        if starts[i] >= ends[i]:
            assert ranges[i] == b""
        else:
            assert ranges[i] == full_contents[starts[i]:ends[i]]


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
        start = int(x[:equals])
        end = int(x[equals + 1:]) + random.randint(0, 10) # adding some jitter.
        return MockRequest(206, full_contents[start:end + 1], {})

    output = b""
    boundary = b"FOOBAR"
    for x in ranges:
        equals = x.find("-")
        start = int(x[:equals])
        end = int(x[equals + 1:]) + random.randint(0, 10) # adding some jitter.
        output += b"--" + boundary + b"\r\nContent-Range: bytes "
        output += str(start).encode("utf-8") + b"-" + str(end).encode("utf-8") + b"/" + str(len(full_contents)).encode("utf-8")
        output += b"\r\n\r\n" + full_contents[start:end + 1] + b"\r\n"
    output += b"--" + boundary + b"--"

    return MockRequest(206, output, { "Content-Type": "multipart/byteranges; boundary=" + boundary.decode("UTF-8") })


def test_download_multipart_ranges():
    full_contents = get_full_contents("9606_collections.tsv")
    url = gesel.database_url() + "/9606_collections.tsv"

    # A simple request to start things off.
    starts = [0, 10, 20]
    ends = [5, 17, 27]
    ranges = gesel.download_multipart_ranges(url, starts, ends, _mock=mock_request)
    for i in range(len(starts)):
        assert ranges[i] == full_contents[starts[i]:ends[i]]

    # Now trying out of order.
    starts = [20, 10, 0]
    ends = [30, 15, 8]
    ranges = gesel.download_multipart_ranges(url, starts, ends, _mock=mock_request)
    for i in range(len(starts)):
        assert ranges[i] == full_contents[starts[i]:ends[i]]

    # Now throwing in some invalid ranges.
    starts = [10, 20, 10, 50, 2]
    ends = [5, 30, 15, 40, 8]
    ranges = gesel.download_multipart_ranges(url, starts, ends, _mock=mock_request)
    for i in range(len(starts)):
        if starts[i] >= ends[i]:
            assert ranges[i] == b""
        else:
            assert ranges[i] == full_contents[starts[i]:ends[i]]

    # Behaves with just a single range, or even no ranges.
    assert gesel.download_multipart_ranges(url, [13], [39], _mock=mock_request) == [full_contents[13:39]]
    assert gesel.download_multipart_ranges(url, [], [], _mock=mock_request) == []


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

    starts, contents = _parse_multipart_response(ex, b"foo") 
    assert starts == [10, 30, 50]
    assert contents == [payload1, payload2, payload3]
