import gesel


def test_fetch_all_genes_local(local_config):
    species = local_config["species"]
    ref_genes = local_config["genes"]
    test_config = local_config["latest"]
    gesel.flush_memory_cache(test_config)

    roundtrip = gesel.fetch_all_genes(species, config = test_config)
    assert roundtrip == ref_genes

    sub = gesel.fetch_all_genes(species, types = ["Bravo"], config = test_config)
    assert sub.get_column_names().as_list() == ["Bravo"]
    assert sub.get_column("Bravo") == ref_genes.get_column("Bravo")

    preloaded = gesel.fetch_all_genes(species, config = test_config)
    assert roundtrip == preloaded


def test_fetch_all_genes_local_v1(local_config):
    species = local_config["species"]
    ref_genes = local_config["genes"]
    test_config_v1 = local_config["gene-v0.1.0"]
    gesel.flush_memory_cache(test_config_v1)

    roundtrip = gesel.fetch_all_genes(species, types = ref_genes.get_column_names(), config=test_config_v1)
    assert roundtrip == ref_genes


def test_fetch_all_genes_remote():
    gesel.flush_memory_cache()

    roundtrip = gesel.fetch_all_genes("9606") 
    assert roundtrip.shape[0] > 0

    for tt in ["symbol", "ensembl", "entrez"]:
        found = 0
        for x in roundtrip[tt]:
            found += len(x) > 0
        assert found > 0

    # Works for a single type as well.
    sym_only = gesel.fetch_all_genes("9606", types=["symbol"]) 
    assert sym_only.get_column_names().as_list() == ["symbol"]
    assert sym_only["symbol"] == roundtrip["symbol"]

    import re
    enslike = re.compile("^(ENSG[0-9]+|LRG_[0-9]+)$")
    for x in roundtrip["ensembl"]:
        for y in x:
            assert enslike.match(y) is not None

    etzlike = re.compile("^[0-9]+$")
    for x in roundtrip["entrez"]:
        for y in x:
            assert etzlike.match(y) is not None

    preloaded = gesel.fetch_all_genes("9606")
    assert roundtrip == preloaded
