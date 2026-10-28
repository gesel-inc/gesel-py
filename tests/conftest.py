import gesel
import biocframe
import random
import tempfile
import pytest

_gene_dir = None
_gene_dir_v1 = None
_db_dir = None


@pytest.fixture(scope="session")
def setup_local_config():
    ref_num_genes = 10000

    # Setting up the gene annotations.
    global _gene_dir
    global _gene_dir_v1
    if _gene_dir is None:
        ref_genes = {}
        ref_gene_types = ["alpha", "bravo", "charlie"]

        for i, tp in enumerate(ref_gene_types):
            gene_ids = [tp  + "_" + str(i) for i in range(19999)]
            curgenes = []
            for g in range(ref_num_genes):
                num = round(random.expovariate(0.4))
                chosen = random.sample(gene_ids, k=num)
                curgenes.append(chosen)
            ref_genes[tp] = curgenes

        bdf = biocframe.BiocFrame(ref_genes)

        _gene_dir = tempfile.mkdtemp()
        gesel.prepare_gene_files(
            species,
            bdf,
            path = _gene_dir,
            version = "0.2.0"
        )

        _gene_dir_v1 = tempfile.mkdtemp()
        gesel.prepare_gene_files(
            species,
            bdf,
            path = _gene_dir_v1,
            version = "0.1.0"
        )

    # Setting up the database files.
    global _db_dir
    if _db_dir is None:
        ref_collections = biocframe.BiocFrame({
            "title": ["FOO", "BAR", "WHEE"],
            "description": ["I am a foo", "I am a bar", "I am a whe"],
            "maintainer": ["Aaron", "Aaron", "Aaron"],
            "source": ["https://foo", "https://bar", "https://whe"]
        })

        ref_set_info = [
            biocframe.BiocFrame({
                "name": ["FOO_" + str(i) for i in range(20)],
                "description": ["this is FOO " + str(i) for i in range(20)]
            }),
            biocframe.BiocFrame({
                "name": ["BAR_" + str(i) for i in range(50)],
                "description": ["this is BAR " + str(i) for i in range(50)]
            }),
            biocframe.BiocFrame({
                "name": ["WHE_" + str(i) for i in range(10)],
                "description": ["this is WHE " + str(i) for i in range(10)]
            })
        ]

        ref_set_membership = []
        for i in range(ref_collections.shape[0]):
            membership = []
            for j in range(ref_set_info[i].shape[0]):
                membership.append(random.sample(range(ref_num_genes), random.sample(range(100), 1)[0]))

        _db_dir = tempfile.mkdtemp()
        gesel.prepare_database_files(
            species,
            ref_collections, 
            ref_set_info, 
            ref_set_membership,
            ref_num_genes,
            db_dir
        )

    test_config = gesel.new_config(
        fetch_gene = lambda name : os.path.join(_gene_dir, name),
        fetch_file = lambda name : os.path.join(_db_dir, name),
        fetch_ranges = lambda name, starts, ends : gesel.read_database_ranges(_db_dir, name, starts, ends)
    )

    test_config_v1 = gesel.new_config(
        fetch_gene = lambda name : os.path.join(_gene_dir_v1, name),
        fetch_file = lambda name : os.path.join(_ref_dir, name),
        fetch_ranges = lambda name, starts, ends : gesel.read_database_ranges(_db_dir, name, starts, ends)
    )

    return { "latest": test_config, "gene-v0.1.0": test_config_v1 }
