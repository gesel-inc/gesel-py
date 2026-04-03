import gesel


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
