import gesel
import tempfile
import os


def test_download_gene_file():
    tmpdir = tempfile.mkdtemp()
    out = gesel.download_gene_file("9606_symbol.tsv.gz", cache=tmpdir)
    assert os.path.exists(out)
    assert os.path.dirname(out) == tmpdir

    with open(out, "w") as f:
        f.write("")
    assert gesel.download_gene_file("9606_symbol.tsv.gz", cache=tmpdir) == out # re-uses the cache.
    assert os.stat(out).st_size == 0 # doesn't change the cached value.

    assert gesel.download_gene_file("9606_symbol.tsv.gz", cache=tmpdir, overwrite=True) == out # re-uses the cache.
    assert os.stat(out).st_size > 0 # overwrites the broken cache value.


def test_gene_url():
    url = gesel.gene_url()
    assert isinstance(url, str)

    old = gesel.gene_url("https://foo.bar")
    assert gesel.gene_url() == "https://foo.bar"

    gesel.gene_url(old)
    assert gesel.gene_url() == url
