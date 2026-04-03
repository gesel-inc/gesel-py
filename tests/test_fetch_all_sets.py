import gesel


def test_fetch_all_sets_remote():
    gesel.flush_memory_cache()
    test = gesel.fetch_all_sets("9606")
    assert test.shape[0] > 0

    for i in range(test.shape[0]):
        assert isinstance(test["name"][i], str)
        assert isinstance(test["description"][i], str)
        assert test["size"][i] > 0

    coll_info = gesel.fetch_all_collections("9606")
    assert test["collection"] == sorted(test["collection"])
    for i in range(test.shape[0]):
        assert i == coll_info["start"][test["collection"][i]] + test["number"][i]

    preloaded = gesel.fetch_all_sets("9606")
    assert test == preloaded
