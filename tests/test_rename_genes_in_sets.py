import gesel
import random


def test_rename_genes_in_sets_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]

    all_sets = gesel.fetch_genes_for_all_sets(species, config=test_config)
    renamed = gesel.rename_genes_in_sets(species, all_sets, "alpha", config=test_config)
    assert len(renamed) == len(all_sets)

    ref_genes = local_config["genes"]["alpha"]
    for s, curset in enumerate(all_sets):
        expected = set()
        for i in curset:
            for nm in ref_genes[i]:
                expected.add(nm)
        assert sorted(expected) == sorted(renamed[s])

    # Removes all duplicates correctly.
    all_sets2 = []
    for curset in all_sets:
        if len(curset):
            all_sets2.append(curset + random.choices(curset, k=100))
        else:
            all_sets2.append(curset)
    renamed2 = gesel.rename_genes_in_sets(species, all_sets2, "alpha", config=test_config)
    assert renamed == renamed2

    # Handles empty sets.
    all_sets2 = [[]] + all_sets + [[]]
    renamed2 = gesel.rename_genes_in_sets(species, all_sets2, "alpha", config=test_config)
    assert renamed2 == [[]] + renamed + [[]]


def test_rename_genes_in_sets_remote():
    alpha_genes = gesel.fetch_all_genes("10090", ["symbol"])["symbol"]

    # Check that it works properly if there's empty sets.
    made_up = [range(10), [], range(2, 100, 2), [], range(500, 1000, 10), []]
    renamed = gesel.rename_genes_in_sets("10090", made_up, "symbol")

    for s, curset in enumerate(made_up):
        expected = set()
        for i in curset:
            for nm in alpha_genes[i]:
                expected.add(nm)
        assert sorted(expected) == sorted(renamed[s])
