import gesel
import tempfile
import os


def test_download_database_file():
    tmpdir = tempfile.mkdtemp()
    out = gesel.download_database_file("9606_collections.tsv.gz", cache=tmpdir)
    assert os.path.exists(out)
    assert os.path.dirname(out) == tmpdir

    with open(out, "w") as f:
        f.write("")
    assert gesel.download_database_file("9606_collections.tsv.gz", cache=tmpdir) == out # re-uses the cache.
    assert os.stat(out).st_size == 0 # doesn't change the cached value.

    assert gesel.download_database_file("9606_collections.tsv.gz", cache=tmpdir, overwrite=True) == out # re-uses the cache.
    assert os.stat(out).st_size > 0 # overwrites the broken cache value.


def test_database_url():
    url = gesel.database_url()
    assert isinstance(url, str)

    old = gesel.database_url("https://foo.bar")
    assert gesel.database_url() == "https://foo.bar"

    gesel.database_url(old)
    assert gesel.database_url() == url
