import gesel


def test_fetch_all_collections_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]
    gesel.flush_memory_cache(test_config)

    sizes = []
    offsets = []
    offset = 0
    for x in local_config["set2gene"]:
        offsets.append(offset)
        sizes.append(len(x))
        offset += len(x)

    payload = gesel.fetch_all_collections(species, config = test_config)
    expected = local_config["collections"]
    assert payload.get_column("title") == expected.get_column("title")
    assert payload.get_column("description") == expected.get_column("description")
    assert payload.get_column("source") == expected.get_column("source")
    assert payload.get_column("maintainer") == expected.get_column("maintainer")
    assert payload.get_column("start") == offsets
    assert payload.get_column("size") == sizes

    # Fetch from cache.
    preloaded = gesel.fetch_all_collections(species, config = test_config)
    assert preloaded == payload


def test_fetch_all_collections_remote():
    gesel.flush_memory_cache()
    test = gesel.fetch_all_collections("9606")
    assert test.shape[0] > 0

    for i in range(test.shape[0]):
        assert isinstance(test["title"][i], str)
        assert isinstance(test["description"][i], str)
        assert isinstance(test["maintainer"][i], str)
        assert isinstance(test["source"][i], str)
        assert isinstance(test["start"][i], int)
        assert isinstance(test["size"][i], int)
        assert i == 0 or test["start"][i] == test["start"][i-1] + test["size"][i-1]

    preloaded = gesel.fetch_all_collections("9606")
    assert test == preloaded # re-uses the exact same cached object.
