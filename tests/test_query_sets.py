import gesel
import pytest
import biocutils


def test_query_sets_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]
    genes = ["CHARLIE_" + str(i) for i in range(50)] + ["alpha_" + str(i) for i in range(50, 100)] + ["Bravo_" + str(i) for i in range(100, 200)]

    out = gesel.query_sets(species, genes = genes, config = test_config)
    all_sets = gesel.fetch_all_sets(species, config = test_config)
    assert out.get_column("name") == biocutils.subset(all_sets.get_column("name"), out.get_column("set"))

    all_coll = gesel.fetch_all_collections(species, config = test_config)
    assert out.get_column("collection") == biocutils.subset(
        all_coll.get_column("title"), 
        biocutils.subset(all_sets.get_column("collection"), out.get_column("set"))
    )
    assert out.has_column("pvalue")

    # Intersects properly with descriptions.
    fout = gesel.query_sets(species, genes = genes, text = "FOO", config = test_config)
    sets_from_genes_only = set(out.get_column("set"))
    for i, x in enumerate(fout.get_column('set')):
        assert x in sets_from_genes_only
        assert "FOO" in fout.get_column("name")[i] or "FOO" in fout.get_column("description")[i]
    assert fout.has_column("pvalue")

    # Handles descriptions by themselves.
    tout = gesel.query_sets(species, text = "FOO", config = test_config)
    for i in range(tout.shape[0]):
        assert "FOO" in tout.get_column("name")[i] or "FOO" in tout.get_column("description")[i]
    assert not tout.has_column("pvalue")

    with pytest.raises(Exception, match="must be provided"):
        gesel.query_sets(species, config = test_config)


def test_query_sets_local_full_genes(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]
    genes = ["CHARLIE_" + str(i) for i in range(50)] + ["alpha_" + str(i) for i in range(50, 100)] + ["Bravo_" + str(i) for i in range(100, 200)]

    xout = gesel.query_sets(species, genes = genes, types = ["CHARLIE", "alpha", "Bravo"], counts_only = False, config = test_config)
    loaded = gesel.fetch_genes_for_some_sets(species, xout.get_column("set"), config = test_config)
    loaded_alpha = gesel.rename_genes_in_sets(species, loaded, "alpha", config = test_config)
    loaded_Bravo = gesel.rename_genes_in_sets(species, loaded, "Bravo", config = test_config)
    loaded_CHARLIE = gesel.rename_genes_in_sets(species, loaded, "CHARLIE", config = test_config)

    xout2 = gesel.query_sets(species, genes = [y.lower() for y in genes], types = ["CHARLIE", "alpha", "Bravo"], counts_only = False, config = test_config)
    for i in range(len(loaded)):
        expected = biocutils.intersect(loaded_alpha[i] + loaded_Bravo[i] + loaded_CHARLIE[i], genes)
        assert sorted(expected) == sorted(xout.get_column("which")[i])
        assert sorted([y.lower() for y in expected]) == sorted(xout2.get_column("which")[i])


def test_query_sets_remote():
    out = gesel.query_sets(
        "9606",
        genes = ["tead1", "tead2", "tead3", "tead4"],
        text = "transcription"
    )
    assert out.shape[0] > 0
    for i in range(out.shape[0]):
        assert "transcription" in out.get_column("name")[i].lower() or "transcription" in out.get_column("description")[i].lower()

    chosen2 = ["SNAP25", "neurod4", "neurod6"]
    out2 = gesel.query_sets(
        "9606",
        genes = chosen2,
        text = "neuro*",
        counts_only = False
    )
    assert out2.shape[0] > 0
    for i in range(out2.shape[0]):
        assert "neuro" in out2.get_column("name")[i].lower() or "neuro" in out2.get_column("description")[i].lower()
        for y in out2.get_column("which")[i]:
            assert y in chosen2
