import gesel
import itertools


def test_fetch_genes_for_all_sets_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]
    gesel.flush_memory_cache(test_config)

    full_set_membership = list(itertools.chain(*local_config["set2gene"]))
    for y in full_set_membership:
        y.sort()

    payload = gesel.fetch_genes_for_all_sets(species, config = test_config)
    assert payload == full_set_membership

    preloaded = gesel.fetch_genes_for_all_sets(species, config = test_config)
    assert payload == preloaded


def test_fetch_genes_for_all_sets_remote():
    gesel.flush_memory_cache()

    test = gesel.fetch_genes_for_all_sets("9606")
    num_genes = gesel.fetch_all_genes("9606", types=["ensembl"]).shape[0]

    num_non_empty = 0
    for gset in test:
        num_non_empty += len(gset) > 0
        previous = -1
        for g in gset:
            assert g >= 0 and g < num_genes
            assert g > previous
            previous = g

    assert num_non_empty > 0

    # Caching works as expected.
    preloaded = gesel.fetch_genes_for_all_sets("9606")
    assert test == preloaded
