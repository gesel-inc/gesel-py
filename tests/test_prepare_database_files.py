import gesel
import copy
import tempfile
import os
import pytest


def test_prepare_database_files_duplicated(local_config):
    # Checking that prepare_database_files prunes out duplicates, resorts indices within each gene set.
    set_membership_dup = copy.deepcopy(local_config["set2gene"])
    for coll in set_membership_dup:
        for i, x in enumerate(coll):
            coll[i] += x[:min(len(x), 5)]

    species = local_config["species"]
    copy_dir = tempfile.mkdtemp()
    gesel.prepare_database_files(
        species,
        local_config["collections"],
        local_config["sets"],
        set_membership_dup,
        local_config["genes"].shape[0],
        copy_dir 
    )

    copy_config = gesel.new_config(
        fetch_gene = local_config["latest"]["fetch_gene"],
        fetch_file = lambda name : os.path.join(copy_dir, name),
        fetch_ranges = lambda name, starts, ends : gesel.read_database_ranges(copy_dir, name, starts, ends)
    )

    test_config = local_config["latest"]
    assert gesel.fetch_all_collections(species, config = copy_config) == gesel.fetch_all_collections(species, config = test_config)
    assert gesel.fetch_all_sets(species, config = copy_config) == gesel.fetch_all_sets(species, config = test_config)
    assert gesel.fetch_genes_for_all_sets(species, config = copy_config) == gesel.fetch_genes_for_all_sets(species, config = test_config)
    assert gesel.fetch_sets_for_all_genes(species, config = copy_config) == gesel.fetch_sets_for_all_genes(species, config = test_config)


def test_prepare_database_files_error(local_config):
    species = local_config["species"]
    copy_dir = tempfile.mkdtemp()

    with pytest.raises(Exception, match="should equal number of rows"):
        gesel.prepare_database_files(
            species,
            local_config["collections"],
            local_config["sets"][:1],
            local_config["set2gene"],
            local_config["genes"].shape[0],
            copy_dir 
        )

    with pytest.raises(Exception, match="should equal number of rows"):
        gesel.prepare_database_files(
            species,
            local_config["collections"],
            local_config["sets"],
            local_config["set2gene"][:1],
            local_config["genes"].shape[0],
            copy_dir 
        )

    sub_membership = copy.deepcopy(local_config["set2gene"])
    sub_membership[2] = sub_membership[2][:5]
    with pytest.raises(Exception, match="should be the same"):
        gesel.prepare_database_files(
            species,
            local_config["collections"],
            local_config["sets"],
            sub_membership,
            local_config["genes"].shape[0],
            copy_dir 
        )

    sub_membership = copy.deepcopy(local_config["set2gene"])
    sub_membership[2][0].append(1e6)
    with pytest.raises(Exception, match="out-of-bounds"):
        gesel.prepare_database_files(
            species,
            local_config["collections"],
            local_config["sets"],
            sub_membership,
            local_config["genes"].shape[0],
            copy_dir 
        )
