import gesel
import biocutils
import biocframe
import itertools
import random


def test_find_overlapping_sets_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]

    full_set_membership = list(itertools.chain(*local_config["set2gene"]))
    genes = random.sample(range(local_config["genes"].shape[0]), 100)
    chosen_genes = set(genes)
    found_idx = []
    found_members = []
    for i, y in enumerate(full_set_membership):
        collected = []
        for x in y:
            if x in chosen_genes:
                collected.append(x)
        found_members.append(sorted(collected))
        if len(collected):
            found_idx.append(i)

    overlaps, present = gesel.find_overlapping_sets(species, genes, counts_only = False, config = test_config)
    expected_set = overlaps.get_column("set")
    assert sorted(expected_set) == sorted(found_idx)
    assert biocutils.subset(found_members, expected_set) == [sorted(x) for x in overlaps.get_column("genes")]

    counts, present = gesel.find_overlapping_sets(species, genes, config = test_config)
    assert counts == biocframe.BiocFrame({ "set": overlaps.get_column("set"), "count": [len(x) for x in overlaps.get_column("genes")] })

    # Automatically removes duplicates from the genes.
    duplicated_c, present = gesel.find_overlapping_sets(species, genes + genes, config = test_config)
    assert counts == duplicated_c
    duplicated_o, present = gesel.find_overlapping_sets(species, genes + genes, counts_only = False, config = test_config)
    assert overlaps == duplicated_o


def test_find_overlapping_sets_remote():
    chosen = list(range(10))
    for i, x in enumerate(chosen):
        chosen[i] = x * 10

    everything = gesel.fetch_genes_for_all_sets("9606")

    chosen_set = set(chosen) 
    collected = []
    keep = []
    for i, genes in enumerate(everything):
        intersected = []
        for y in genes:
            if y in chosen_set:
                intersected.append(y)
        collected.append(intersected)
        if len(intersected) > 0:
            keep.append(i)

    overlaps, present = gesel.find_overlapping_sets("9606", chosen, counts_only=False)
    assert sorted(overlaps["set"]) == sorted(keep)

    expected = [sorted(y) for y in biocutils.subset(collected, overlaps["set"])]
    observed = [sorted(y) for y in overlaps["genes"]]
    assert expected == observed

    counts, present2 = gesel.find_overlapping_sets("9606", chosen)
    assert counts["set"] == overlaps["set"]
    assert counts["count"] == [len(y) for y in overlaps["genes"]]
    assert present == present2
