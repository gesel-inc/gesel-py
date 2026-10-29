import gesel


def test_fetch_gene_version_local(local_config):
    species = local_config["species"]
    test_config = local_config["latest"]
    gesel.flush_memory_cache(test_config)

    assert gesel.fetch_gene_version(species, test_config) == "0.2.0"
    assert gesel.fetch_gene_version(species, test_config) == "0.2.0" # pulls from cache

    test_config_v1 = local_config["gene-v0.1.0"]
    gesel.flush_memory_cache(test_config_v1)
    assert gesel.fetch_gene_version(species, test_config_v1) == "0.1.0"
    assert gesel.fetch_gene_version(species, test_config_v1) == "0.1.0" # pulls from cache


def test_fetch_gene_version_remote():
    gesel.flush_memory_cache()

    assert gesel.fetch_gene_version("9606") == "0.2.0"
    assert gesel.fetch_gene_version("9606") == "0.2.0" # pulls from cache.
    assert gesel.fetch_gene_version("123") == "0.1.0" # falls back if no version file is available.
