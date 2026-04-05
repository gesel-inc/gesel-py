import gesel


def test_search_genes_remote():
    chosen = [ "SNAP25", "neurod6", "ENSG00000139618", "10023" ]

    out = gesel.search_genes("9606", chosen)
    assert len(out) == len(chosen)
    for x in out:
        assert len(x) > 0

    all_genes = gesel.fetch_all_genes("9606")
    for i in out[0]:
        assert "SNAP25" in all_genes["symbol"][i]
    for i in out[1]:
        assert "NEUROD6" in all_genes["symbol"][i]
    for i in out[2]:
        assert "ENSG00000139618" in all_genes["ensembl"][i]
    for i in out[3]:
        assert "10023" in all_genes["entrez"][i]

    out2 = gesel.search_genes("9606", chosen, ignore_case=False)
    assert len(out2[1]) == 0 # no hits for lower-case NEUROD6.
