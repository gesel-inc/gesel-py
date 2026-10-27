import gesel


def test_fetch_gene_types_remote():
    assert sorted(gesel.fetch_gene_types("9606")) == ["ensembl", "entrez", "symbol"] 
    assert sorted(gesel.fetch_gene_types("9606")) == ["ensembl", "entrez", "symbol"] # works again from cache.
