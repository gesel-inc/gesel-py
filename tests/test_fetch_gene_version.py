import gesel


def test_gene_version_remote():
    assert gesel.fetch_gene_version("9606") == "0.2.0"
    assert gesel.fetch_gene_version("9606") == "0.2.0" # pulls from cache.
    assert gesel.fetch_gene_version("123") == "0.1.0" # falls back if no version file is available.
