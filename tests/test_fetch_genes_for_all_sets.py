import gesel


def test_fetch_genes_for_all_sets_remote():
    test = gesel.fetch_genes_for_all_sets("9606")
    num_genes = gesel.fetch_all_genes("9606", types=["ensembl"]).shape[0]

    num_non_empty = 0
    for gset in test:
        num_non_empty += len(gset) > 0
        previous = -1
        for g in gset:
            assert g >= 0 and g < num_genes
            assert g > previous
            previous = g

    assert num_non_empty > 0

    # Caching works as expected.
    preloaded = gesel.fetch_genes_for_all_sets("9606")
    assert test == preloaded
