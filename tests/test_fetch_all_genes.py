import gesel


def test_fetch_all_genes_remote():
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
