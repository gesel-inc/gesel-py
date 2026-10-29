import gesel
import random

def test_fetch_some_collections_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]

    # Load all collections for reference comparison.
    # However, we need to make sure we flush the cache so that range requests are actually performed.
    everything = gesel.fetch_all_collections(species, config = test_config)
    gesel.flush_memory_cache(test_config)

    payload = gesel.fetch_some_collections(species, [0], config = test_config)
    assert payload == everything[[0],:]

    # Cache is not used.
    payload = gesel.fetch_some_collections(species, [1], config = test_config)
    assert payload == everything[[1],:]

    # Works with partial caching.
    chosen  = range(everything.shape[0])
    payload = gesel.fetch_some_collections(species, chosen, config = test_config)
    assert payload == everything

    # Works with full caching
    payload = gesel.fetch_some_collections(species, [2, 1], config = test_config)
    assert payload == everything[[2,1],:]

    # Works for sizes.
    sizes = gesel.fetch_collection_sizes(species, config = test_config)
    assert sizes == everything.get_column("size")

    # Works with pre-loaded.
    everything = gesel.fetch_all_collections(species, config = test_config)
    preloaded = gesel.fetch_some_collections(species, [2, 0, 1], config = test_config)
    assert preloaded == everything[[2, 0, 1],:]

    sizes = gesel.fetch_collection_sizes(species, config = test_config)
    assert sizes == everything.get_column("size")


def test_fetch_some_collections_remote():
    everything = gesel.fetch_all_collections("9606")
    gesel.flush_memory_cache()

    chosen0 = set([0, everything.shape[0] - 1])
    for i in range(5):
        chosen0.add(random.randint(0, everything.shape[0] - 1))
    chosen = list(chosen0)

    test = gesel.fetch_some_collections("9606", chosen)
    expected = everything[chosen,:]
    assert test.get_column_names() == expected.get_column_names()
    for col in test.get_column_names():
        assert test[col] == expected[col]

    assert everything["size"] == gesel.fetch_collection_sizes("9606")

    # Works with partial caching.
    preloaded = gesel.fetch_some_collections("9606", chosen)
    for col in test.get_column_names():
        assert test[col] == preloaded[col]

    extras = []
    for y in range(everything.shape[0]):
        if y not in chosen0:
            extras.append(y)
            if len(extras) == 10:
                break

    reloaded_plus = gesel.fetch_some_collections("9606", chosen + extras)
    plus = gesel.fetch_some_collections("9606", extras)
    for col in test.get_column_names():
        assert test[col] + plus[col] == reloaded_plus[col]

    # Works with full caching.
    gesel.fetch_all_collections("9606")
    preloaded = gesel.fetch_some_collections("9606", chosen)
    for col in test.get_column_names():
        assert test[col] == preloaded[col]
