import gesel
import compressed_lists


def test_load_all_sets_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]

    loaded_sets, loaded_details = gesel.load_all_sets(species, "alpha", config=test_config)
    assert len(loaded_sets) == loaded_details.shape[0]
    assert loaded_sets.get_names().as_list() == loaded_details.get_column("name")
    for i in loaded_sets:
        for j in i:
            assert j.startswith("alpha_")

    loaded_comp = gesel.load_all_sets(species, "alpha", config=test_config, as_compressed = True)
    assert isinstance(loaded_comp, compressed_lists.CompressedList)
    assert loaded_comp.as_list() == loaded_sets.as_list()
    assert loaded_comp.get_element_metadata() == loaded_details.set_row_names(None)


def test_load_all_sets_remote():
    loaded_sets, loaded_details = gesel.load_all_sets("7227", "symbol")
    assert len(loaded_sets) == loaded_details.shape[0]

    loaded_comp = gesel.load_all_sets("7227", "symbol", as_compressed = True)
    assert isinstance(loaded_comp, compressed_lists.CompressedList)
    assert loaded_comp.as_list() == loaded_sets.as_list()
    assert loaded_comp.get_element_metadata() == loaded_details.set_row_names(None)
