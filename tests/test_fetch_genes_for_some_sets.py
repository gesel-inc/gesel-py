import gesel
import random
import biocutils


def test_fetch_genes_for_some_sets_remote():
    everything = gesel.fetch_genes_for_all_sets("9606")
    gesel.flush_memory_cache()

    chosen0 = set([0, len(everything) - 1])
    for i in range(20):
        chosen0.add(random.randint(0, len(everything) - 1))
    chosen = list(chosen0)

    test = gesel.fetch_genes_for_some_sets("9606", chosen)
    expected = biocutils.subset(everything, chosen)
    assert test == expected

    # Works with partial caching.
    preloaded = gesel.fetch_genes_for_some_sets("9606", chosen)
    assert test == preloaded

    extras = []
    for y in range(len(everything)):
        if y not in chosen0:
            extras.append(y)
            if len(extras) == 10:
                break

    reloaded_plus = gesel.fetch_genes_for_some_sets("9606", chosen + extras)
    plus = gesel.fetch_genes_for_some_sets("9606", extras)
    assert test + plus == reloaded_plus

    # Works with full caching.
    gesel.fetch_genes_for_all_sets("9606")
    reloaded = gesel.fetch_genes_for_some_sets("9606", chosen)
    assert test == reloaded
