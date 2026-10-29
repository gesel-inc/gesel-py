import gesel
import itertools


def test_search_genes_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]
    ref_genes = local_config["genes"]

    def get_first(col):
        for x in col:
            for y in x:
                return y
    chosen = [
        get_first(ref_genes.get_column("alpha")),
        get_first(ref_genes.get_column("Bravo")),
        get_first(ref_genes.get_column("CHARLIE"))
    ]

    out = gesel.search_genes(species, chosen, config = test_config) 
    assert len(out) == len(chosen)
    assert all([len(x) for x in out])

    for i in out[0]:
        assert chosen[0] in ref_genes.get_column("alpha")[i]
    for i in out[1]:
        assert chosen[1] in ref_genes.get_column("Bravo")[i]
    for i in out[2]:
        assert chosen[2] in ref_genes.get_column("CHARLIE")[i]

    # Same result when types are requested specifically. 
    typed = gesel.search_genes(species, chosen, types = ref_genes.get_column_names(), config = test_config) 
    assert out == typed

    # Works after ignoring case.
    lout = gesel.search_genes(species, [x.lower() for x in chosen], ignore_case = True, config = test_config)
    assert out == lout


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
