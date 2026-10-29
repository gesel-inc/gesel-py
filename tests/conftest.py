import gesel
import biocframe
import random
import tempfile
import pytest
import os


@pytest.fixture(scope="session")
def local_config():
    collected = {}

    ref_species = "1234"
    collected["species"] = ref_species

    ref_num_genes = 10000
    collected["num_genes"] = ref_num_genes

    # Setting up the gene annotations.
    ref_genes = {}
    ref_gene_types = ["alpha", "Bravo", "CHARLIE"]

    for i, tp in enumerate(ref_gene_types):
        gene_ids = [tp  + "_" + str(i) for i in range(ref_num_genes)]
        genes_plus = int(ref_num_genes * (1 + i/5)) # generating a 1:many mapping of genes to names.
        chosen = random.choices(gene_ids, k=genes_plus)
        ids = random.choices(range(ref_num_genes), k=genes_plus)
        curgenes = []
        for j in range(ref_num_genes):
            curgenes.append([])
        for j in range(genes_plus):
            curgenes[ids[j]].append(chosen[j])
        ref_genes[tp] = curgenes

    ref_bdf = biocframe.BiocFrame(ref_genes)
    collected["genes"] = ref_bdf

    gene_dir = tempfile.mkdtemp()
    gesel.prepare_gene_files(
        ref_species,
        ref_bdf,
        path = gene_dir,
        version = "0.2.0"
    )

    gene_dir_v1 = tempfile.mkdtemp()
    gesel.prepare_gene_files(
        ref_species,
        ref_bdf,
        path = gene_dir_v1,
        version = "0.1.0"
    )

    # Setting up the database files.
    ref_collections = biocframe.BiocFrame({
        "title": ["FOO", "BAR", "WHEE"],
        "description": ["I am a foo", "I am a bar", "I am a whe"],
        "maintainer": ["Aaron", "Aaron", "Aaron"],
        "source": ["https://foo", "https://bar", "https://whe"]
    })
    collected["collections"] = ref_collections

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
    collected["sets"] = ref_set_info 

    ref_set_membership = []
    for i in range(ref_collections.shape[0]):
        membership = []
        for j in range(ref_set_info[i].shape[0]):
            membership.append(random.sample(range(ref_num_genes), random.sample(range(100), 1)[0]))
        ref_set_membership.append(membership)
    collected["set2gene"] = ref_set_membership

    db_dir = tempfile.mkdtemp()
    gesel.prepare_database_files(
        ref_species,
        ref_collections, 
        ref_set_info, 
        ref_set_membership,
        ref_num_genes,
        db_dir
    )

    collected["latest"] = gesel.new_config(
        fetch_gene = lambda name : os.path.join(gene_dir, name),
        fetch_file = lambda name : os.path.join(db_dir, name),
        fetch_ranges = lambda name, starts, ends : gesel.read_database_ranges(db_dir, name, starts, ends)
    )

    collected["gene-v0.1.0"] = gesel.new_config(
        fetch_gene = lambda name : os.path.join(gene_dir_v1, name),
        fetch_file = lambda name : os.path.join(db_dir, name),
        fetch_ranges = lambda name, starts, ends : gesel.read_database_ranges(db_dir, name, starts, ends)
    )

    return collected
