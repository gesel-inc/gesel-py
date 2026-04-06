import gesel


def test_cache_directory():
    assert isinstance(gesel.cache_directory(), str)
    old = gesel.cache_directory("/tmp/foo/bar")
    assert gesel.cache_directory() == "/tmp/foo/bar"
    gesel.cache_directory(old)
    assert gesel.cache_directory() == old
