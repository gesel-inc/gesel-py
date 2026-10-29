import gesel
import random
import biocutils


def test_fetch_genes_for_some_sets_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]

    # Load all gene sets for reference comparison.
    # However, we need to make sure we flush the cache so that range requests are actually performed.
    everything = gesel.fetch_sets_for_all_genes(species, config = test_config)
    gesel.flush_memory_cache(test_config)

    sub = range(1, len(everything), 3)
    payload = gesel.fetch_sets_for_some_genes(species, sub, config = test_config) 
    assert biocutils.subset(everything, sub) == payload

    # Subsequent requests with no caching. 
    sub = range(0, len(everything), 3)
    payload = gesel.fetch_sets_for_some_genes(species, sub, config = test_config) 
    assert biocutils.subset(everything, sub) == payload

    # Works with partial caching (we need new requests for range(2, len(everything), 3)).
    together = range(len(everything))
    payload = gesel.fetch_sets_for_some_genes(species, together, config = test_config)
    assert everything == payload

    # Works with full caching.
    sub = range(2, len(everything), 3)
    payload = gesel.fetch_sets_for_some_genes(species, sub, config = test_config) 
    assert biocutils.subset(everything, sub) == payload

    # Works with pre-loading.
    everything = gesel.fetch_sets_for_all_genes(species, config = test_config)
    preloaded = gesel.fetch_sets_for_some_genes(species, together, config = test_config)
    assert everything == preloaded


def test_fetch_sets_for_some_genes_remote():
    everything = gesel.fetch_sets_for_all_genes("9606")
    gesel.flush_memory_cache()

    chosen0 = set([0, len(everything) - 1])
    for i in range(20):
        chosen0.add(random.randint(0, len(everything) - 1))
    chosen = list(chosen0)

    test = gesel.fetch_sets_for_some_genes("9606", chosen)
    expected = biocutils.subset(everything, chosen)
    assert test == expected

    # Works with partial caching.
    preloaded = gesel.fetch_sets_for_some_genes("9606", chosen)
    assert test == preloaded

    extras = []
    for y in range(len(everything)):
        if y not in chosen0:
            extras.append(y)
            if len(extras) == 10:
                break

    reloaded_plus = gesel.fetch_sets_for_some_genes("9606", chosen + extras)
    plus = gesel.fetch_sets_for_some_genes("9606", extras)
    assert test + plus == reloaded_plus

    # Works with full caching.
    gesel.fetch_sets_for_all_genes("9606")
    reloaded = gesel.fetch_sets_for_some_genes("9606", chosen)
    assert test == reloaded


def test_effective_number_of_genes_remote():
    gesel.flush_memory_cache()

    out = gesel.effective_number_of_genes("9606")
    gesel.fetch_sets_for_all_genes("9606")
    alt = gesel.effective_number_of_genes("9606")
    assert out == alt
