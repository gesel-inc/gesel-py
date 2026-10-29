import gesel
import biocutils
import re


def test_search_set_text_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]

    # Load all set information as a reference.
    # We need to flush this to ensure that the range requests actually work for the tokens.
    full_set_info = gesel.fetch_all_sets(species, config = test_config)
    gesel.flush_memory_cache(test_config)

    out = gesel.search_set_text(species, "foo 1", config = test_config)
    assert out == list(biocutils.which([x.lower().endswith("foo 1") for x in full_set_info.get_column("description")]))

    # Name or description only.
    nout = gesel.search_set_text(species, "this", use_description = False, config = test_config)
    assert len(nout) == 0

    nout = gesel.search_set_text(species, "this", use_name = False, config = test_config)
    assert nout == list(biocutils.which([x.lower().startswith("this") for x in full_set_info.get_column("description")]))

    nout = gesel.search_set_text(species, "this", use_description = False, use_name = False, config = test_config)
    assert len(nout) == 0

    # Throwing in some wildcards.
    pout = gesel.search_set_text(species, "foo 1*", config = test_config)
    rex = re.compile("foo 1", re.IGNORECASE)
    assert pout == list(biocutils.which([rex.search(x) for x in full_set_info.get_column("description")]))

    pout = gesel.search_set_text(species, "foo ?", config = test_config)
    rex = re.compile("foo .$", re.IGNORECASE)
    assert pout == list(biocutils.which([rex.search(x) for x in full_set_info.get_column("description")]))


def test_search_set_text_remote():
    sets = gesel.fetch_all_sets("9606")
    gesel.flush_memory_cache()

    cout = gesel.search_set_text("9606", "cancer")
    cmatcher = re.compile("cancer", re.I)
    for c in cout:
        assert cmatcher.search(sets["name"][c]) or cmatcher.search(sets["description"][c])

    # Two words, one of which has a prefixed wildcard:
    iout = gesel.search_set_text("9606", "innate immun*")
    imatcher1 = re.compile("innate", re.I)
    imatcher2 = re.compile("immun.*", re.I)
    for i in iout:
        assert imatcher1.search(sets["name"][i]) or imatcher1.search(sets["description"][i])
        assert imatcher2.search(sets["name"][i]) or imatcher2.search(sets["description"][i])

    # Trying with only the name or description (also tests the cache).
    iout_noname = gesel.search_set_text("9606", "immun*", use_name = False)
    for i in iout_noname:
        assert imatcher2.search(sets["description"][i])

    iout_nodesc = gesel.search_set_text("9606", "immun*", use_description = False)
    for i in iout_nodesc:
        assert imatcher2.search(sets["description"][i])

    iout_none = gesel.search_set_text("9606", "immun*", use_description = False, use_name = False)
    assert iout_none == []

    # Non-prefixed wildcard.
    nout = gesel.search_set_text("9606", "*nucleic*")
    nmatcher = re.compile(".*nucleic.*", re.I)
    for n in nout:
        assert nmatcher.search(sets["name"][n]) or nmatcher.search(sets["description"][n])

    # Trying a rare question mark.
    tout = gesel.search_set_text("9606", "?typical")
    tmatcher = re.compile(".typical", re.I)
    for t in tout:
        assert tmatcher.search(sets["name"][t]) or tmatcher.search(sets["description"][t])
