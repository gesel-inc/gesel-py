import gesel
import biocutils
import itertools


def test_fetch_all_sets_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]
    gesel.flush_memory_cache(test_config)

    ref_set_info = local_config["sets"]
    ref_set = biocutils.combine_rows(*ref_set_info)

    payload = gesel.fetch_all_sets(species, config = test_config)
    assert payload.get_column("name") == ref_set.get_column("name")
    assert payload.get_column("description") == ref_set.get_column("description")
    assert payload.get_column("size") == list(itertools.chain(*[[len(x) for x in y] for y in local_config["set2gene"]]))
    assert payload.get_column("collection") == list(itertools.chain(*[[i] * x.shape[0] for i, x in enumerate(ref_set_info)]))
    assert payload.get_column("number") == list(itertools.chain(*[range(x.shape[0]) for x in ref_set_info]))

    # Works when cached.
    preloaded = gesel.fetch_all_sets(species, config = test_config)
    assert payload == preloaded


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
