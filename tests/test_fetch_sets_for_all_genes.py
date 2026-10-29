import gesel
import itertools


def test_fetch_sets_for_all_genes_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]
    gesel.flush_memory_cache(test_config)

    mapping = []
    num_genes = local_config["genes"].shape[0]
    for g in range(num_genes):
        mapping.append([])
    for i, setmem in enumerate(itertools.chain(*local_config["set2gene"])):
        for x in setmem:
            mapping[x].append(i)
    for x in mapping:
        x.sort()

    payload = gesel.fetch_sets_for_all_genes(species, test_config)
    assert mapping == payload

    # Works from cache
    payload = gesel.fetch_sets_for_all_genes(species, test_config)
    assert mapping == payload


def test_fetch_sets_for_all_genes_remote():
    gesel.flush_memory_cache()

    test = gesel.fetch_sets_for_all_genes("9606")
    num_sets = gesel.fetch_all_sets("9606").shape[0]

    num_non_empty = 0
    for gmap in test:
        num_non_empty += len(gmap) > 0
        previous = -1
        for s in gmap:
            assert s >= 0 and s < num_sets 
            assert s > previous
            previous = s 

    assert num_non_empty > 0

    # Caching works as expected.
    preloaded = gesel.fetch_sets_for_all_genes("9606")
    assert test == preloaded
