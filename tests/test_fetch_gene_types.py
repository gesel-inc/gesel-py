import gesel


def test_fetch_gene_types_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]
    gesel.flush_memory_cache(test_config)

    expected = local_config["genes"].get_column_names().as_list()
    assert gesel.fetch_gene_types(species, test_config) == expected
    assert gesel.fetch_gene_types(species, test_config) == expected # works again from cache.

    test_config_v1 = local_config["gene-v0.1.0"]
    gesel.flush_memory_cache(test_config_v1)
    assert gesel.fetch_gene_types(species, test_config_v1) == ["ensembl", "entrez", "symbol"]


def test_fetch_gene_types_remote():
    gesel.flush_memory_cache()

    assert sorted(gesel.fetch_gene_types("9606")) == ["ensembl", "entrez", "symbol"] 
    assert sorted(gesel.fetch_gene_types("9606")) == ["ensembl", "entrez", "symbol"] # works again from cache.
