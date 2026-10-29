import gesel
import random
import itertools


def test_create_gene_identifier_map_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]
    gesel.flush_memory_cache(test_config)

    def test_Bravo(): 
        mapping = gesel.create_gene_identifier_map(species, type = "Bravo", config = test_config)
        assert list(mapping.keys())[0].startswith("Bravo_")

        current_names = list(set(itertools.chain(*local_config["genes"]["Bravo"])))
        assert len(mapping) == len(current_names)

        # Randomly sample a gene to check.
        for x in random.sample(current_names, 20):
            current = set()
            for i, y in enumerate(local_config["genes"]["Bravo"]):
                for z in y:
                    if z == x:
                        current.add(i)
            assert sorted(list(current)) == sorted(mapping[x])

        # Retrieves from cache correctly.
        assert mapping == gesel.create_gene_identifier_map(species, type = "Bravo", config = test_config)

    test_Bravo()

    # Works when ignoring the case.
    def test_CHARLIE():
        lmapping = gesel.create_gene_identifier_map(species, type = "CHARLIE", ignore_case = True, config = test_config)
        assert list(lmapping.keys())[0].startswith("charlie_")

        current_names = list(set(x.lower() for x in itertools.chain(*local_config["genes"]["CHARLIE"])]))
        assert len(lmapping) == len(current_names)

        # Randomly sample a gene to check.
        for x in random.sample(current_names, 20):
            x = x.lower()
            current = set()
            for i, y in enumerate(local_config["genes"]["CHARLIE"]):
                for z in y:
                    if z.lower() == x:
                        current.add(i)
            assert sorted(list(current)) == sorted(lmapping[x])

    test_CHARLIE()


def test_create_gene_identifier_map_remote():
    gesel.flush_memory_cache()
    genes = gesel.fetch_all_genes("9606")

    mapping = gesel.create_gene_identifier_map("9606", type="symbol") 
    assert len(mapping["SNAP25"]) > 0
    for f in mapping["SNAP25"]:
        assert "SNAP25" in genes["symbol"][f]

    emapping = gesel.create_gene_identifier_map("9606", type="ensembl") 
    assert len(emapping["ENSG00000000003"]) > 0
    for f in emapping["ENSG00000000003"]:
        assert "ENSG00000000003" in genes["ensembl"][f]

    # Works when ignoring the case.
    lmapping = gesel.create_gene_identifier_map("9606", type="symbol", ignore_case=True) 
    assert len(lmapping["neurod6"]) > 0
    for f in lmapping["neurod6"]:
        assert "NEUROD6" in genes["symbol"][f]

    # Fetches it from the cache.
    # We use the old name just to get some coverage on the deprecated function.
    reloaded = gesel.map_genes_by_name("9606", type="symbol") 
    assert reloaded == mapping
