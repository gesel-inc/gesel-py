import gesel
import biocutils


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
