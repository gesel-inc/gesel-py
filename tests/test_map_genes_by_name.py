import gesel


def test_map_genes_by_name_remote():
    genes = gesel.fetch_all_genes("9606")

    mapping = gesel.map_genes_by_name("9606", type="symbol") 
    assert len(mapping["SNAP25"]) > 0
    for f in mapping["SNAP25"]:
        assert "SNAP25" in genes["symbol"][f]

    emapping = gesel.map_genes_by_name("9606", type="ensembl") 
    assert len(emapping["ENSG00000000003"]) > 0
    for f in emapping["ENSG00000000003"]:
        assert "ENSG00000000003" in genes["ensembl"][f]

    # Works when ignoring the case.
    lmapping = gesel.map_genes_by_name("9606", type="symbol", ignore_case=True) 
    assert len(lmapping["neurod6"]) > 0
    for f in lmapping["neurod6"]:
        assert "NEUROD6" in genes["symbol"][f]

    # Fetches it from the cache.
    reloaded = gesel.map_genes_by_name("9606", type="symbol") 
    assert reloaded == mapping
