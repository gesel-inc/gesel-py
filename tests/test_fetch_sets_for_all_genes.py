import gesel


def test_fetch_sets_for_all_genes_remote():
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
