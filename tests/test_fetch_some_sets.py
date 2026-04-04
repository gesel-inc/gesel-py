import gesel
import random


def test_fetch_some_sets_remote():
    everything = gesel.fetch_all_sets("9606")
    gesel.flush_memory_cache()

    chosen0 = set([0, everything.shape[0] - 1])
    for i in range(20):
        chosen0.add(random.randint(0, everything.shape[0] - 1))
    chosen = list(chosen0)

    test = gesel.fetch_some_sets("9606", chosen)
    expected = everything[chosen,:]
    assert test.get_column_names() == expected.get_column_names()
    for col in test.get_column_names():
        assert test[col] == expected[col]

    assert everything["size"] == gesel.fetch_set_sizes("9606")

    # Works with partial caching.
    preloaded = gesel.fetch_some_sets("9606", chosen)
    for col in test.get_column_names():
        assert test[col] == preloaded[col]

    extras = []
    for y in range(everything.shape[0]):
        if y not in chosen0:
            extras.append(y)
            if len(extras) == 10:
                break

    reloaded_plus = gesel.fetch_some_sets("9606", chosen + extras)
    plus = gesel.fetch_some_sets("9606", extras)
    for col in test.get_column_names():
        assert test[col] + plus[col] == reloaded_plus[col]

    # Works with full caching.
    gesel.fetch_all_sets("9606")
    preloaded = gesel.fetch_some_sets("9606", chosen)
    for col in test.get_column_names():
        assert test[col] == preloaded[col]
