from typing import Optional
import os
import biocframe
import biocutils

from ._validate_database_files import validate_database_files


def prepare_database_files(
    species: str,
    collections: biocframe.BiocFrame,
    set_info: list,
    set_membership: list,
    num_genes: int,
    path: str = ".",
    validate: bool = True
) -> None:
    """
    Prepare Gesel database files from various pieces of gene set information.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        collections:
            A :py:class:`~biocframe.BiocFrame` of information about each gene set collection, where each row corresponds to a collection.
            This should contain the ``title``, ``description``, ``source`` and ``maintainer`` columns as described in :py:func:`~gesel.fetch_all_collections`.

        set_info:
            List of :py:class:`~biocframe.BiocFrame` objects of length equal to ``len(collections)``.
            Each :py:class:`~biocframe.BiocFrame` corresponds to a collection where each row corresponds to a gene set.
            Each :py:class:`~biocframe.BiocFrame` should have the ``name`` and ``description`` columns as described in :py:func:`~gesel.fetch_all_sets`.

        set_membership:
            List of lists of lists of integers.
            Each middle list ``set_membership[i]`` corresponds to the ``i``-th collection.
            Each of its inner lists ``set_membership[i][j]`` corresponds to the ``j``-th gene set in the ``i``-th collection.
            Each inner list contains the identities of the constituent genes in that set.
            Each gene is identified as a row index into the :py:class:`~biocframe.BiocFrame` returned by :py:func:`~gesel.fetch_all_genes`.
            All gene indices should be positive and no greater than ``num_genes``.
            Inner lists may be unsorted and contain duplicate entries - sorting and deduplication will be performed internally.

        num_genes:
            Total number of genes available for this species.

        path:
            Path to a directory in which to create the database files.

        validate:
            Whether to run :py:func:`~gesel.validate_database_files` on the newly created files.

    Returns:
        Several files are produced inside ``path`` with the ``species_`` prefix.
        ``None`` is returned.

    Examples:
        >>> import biocframe
        >>> collections = biocframe.BiocFrame({
        ...     "title": ["FOO", "BAR"],
        ...     "description": ["I am a foo", "I am a bar"],
        ...     "maintainer": ["Aaron", "Aaron"],
        ...     "source": ["https://foo", "https://bar"]
        ... })
        >>>
        >>> set_info = [
        ...     biocframe.BiocFrame({
        ...         "name": ["FOO_" + str(i) for i in range(20)],
        ...         "description": ["this is FOO " + str(i) for i in range(20)]
        ...     }),
        ...     biocframe.BiocFrame({
        ...         "name": ["BAR_" + str(i) for i in range(50)],
        ...         "description": ["this is BAR " + str(i) for i in range(50)]
        ...     })
        ... ]
        >>>
        >>> num_genes = 10000
        >>> import random
        >>> set_membership = [
        ...     [random.sample(range(num_genes), random.sample(range(500), 1)[0]) for i in range(20)],
        ...     [random.sample(range(num_genes), random.sample(range(200), 1)[0]) for i in range(50)]
        ... ]
        >>>
        >>> import tempfile
        >>> output = tempfile.mkdtemp()
        >>> import gesel
        >>> gesel.prepare_database_files(
        ...     "1234",
        ...     collections, 
        ...     set_info, 
        ...     set_membership,
        ...     num_genes,
        ...     output
        ... )
        >>>
        >>> import os
        >>> config = gesel.new_config(fetch_file = lambda x : os.path.join(output, x))
        >>> print(gesel.fetch_all_sets("1234", config = config))
    """

    num_collections = collections.shape[0]
    if num_collections != len(set_info):
        raise ValueError("length of 'set_info' should equal number of rows in 'collections'")
    if num_collections != len(set_membership):
        raise ValueError("length of 'set_membership' should equal number of rows in 'collections'")

    num_sets = []
    for c in range(num_collections):
        col_size = set_info[c].shape[0]
        if col_size != len(set_membership[c]):
            raise ValueError("number of sets in each collection of 'set_info' and 'set_membership' should be the same")
        num_sets.append(col_size)

    prefix = os.path.join(path, species + "_")

    save_data_frame_with_sizes(
        biocframe.BiocFrame({
            "title": collections.get_column("title"),
            "description": collections.get_column("description"),
            "species": [species] * num_collections,
            "maintainer": collections.get_column("maintainer"),
            "source": collections.get_column("source")
        }), 
        prefix + "collections.tsv",
        num_sets
    )

    set_info = biocutils.combine_rows(*set_info)
    set_membership = biocutils.combine(*set_membership)
    set_sizes = []
    for s, members in enumerate(set_membership):
        cleaned = sorted(list(set(members)))
        set_membership[s] = cleaned
        set_sizes.append(len(cleaned))
    save_data_frame_with_sizes(
        biocframe.BiocFrame({
            "name": set_info.get_column("name"),
            "description": set_info.get_column("description")
        }), 
        prefix + "sets.tsv",
        set_sizes
    )
    save_integer_list(set_membership, prefix + "set2gene.tsv")

    genes2set = []
    for g in range(num_genes):
        genes2set.append([])
    for s, members in enumerate(set_membership):
        for g in members:
            if g < 0 or g >= num_genes:
                raise ValueError("detected out-of-bounds gene indices in 'set_membership'")
            genes2set[g].append(s)
    save_integer_list(genes2set, prefix + "gene2set.tsv")

    # Build a search index for the descriptions and names.
    dtoken_names, dtoken_indices = tokenize(set_info.get_column("description"))
    ntoken_names, ntoken_indices = tokenize(set_info.get_column("name"))
    save_integer_list(ntoken_indices, prefix + "tokens-names.tsv", names=ntoken_names)
    save_integer_list(dtoken_indices, prefix + "tokens-descriptions.tsv", names=dtoken_names)

    if validate:
        validate_database_files(path, species, num_genes)


def save_integer_list(x: list, prefix: str, names: Optional[list] = None) -> None:
    import gzip
    lengths = []
    with open(prefix, "wb") as handle, gzip.open(prefix + ".gz", "wb") as gzhandle:
        for i, vec in enumerate(x):
            msg = ""
            if len(vec):
                # Assume we're already sorted and unique, then get to 0-based indexing with delta encoding.
                msg = str(vec[0])
                for j in range(1, len(vec)):
                    msg += "\t" + str(vec[j] - vec[j - 1])
            msg += "\n"
            msg = msg.encode("UTF-8")
            handle.write(msg)
            gzhandle.write(msg)
            lengths.append(len(msg) - 1) # don't include the newline in this length

    with gzip.open(prefix + ".ranges.gz", "wb") as rhandle:
        if not names:
            for ln in lengths:
                rhandle.write((str(ln) + "\n").encode("UTF-8"))
        else:
            for i, ln in enumerate(lengths):
                rhandle.write((names[i] + "\t" + str(ln) + "\n").encode("UTF-8"))


def save_data_frame_with_sizes(x: biocframe.BiocFrame, prefix: str, size: list) -> None:
    import re 
    subber = re.compile("\t|\n")

    import gzip
    lengths = []
    all_cols = x.get_columns()
    with open(prefix, "wb") as handle, gzip.open(prefix + ".gz", "wb") as gzhandle:
        for r in range(x.shape[0]):
            msg = subber.sub(" ", all_cols[0][r])
            for c in range(1, len(all_cols)):
                msg += "\t" + subber.sub(" ", all_cols[c][r])
            gzhandle.write((msg + "\t" + str(size[r]) + "\n").encode("UTF-8"))
            msg += "\n"
            msg = msg.encode("UTF-8")
            handle.write(msg)
            lengths.append(len(msg) - 1) # don't include the newline in this length

    with gzip.open(prefix + ".ranges.gz", "wb") as rhandle:
        for i, ln in enumerate(lengths):
            rhandle.write((str(ln) + "\t" + str(size[i]) + "\n").encode("UTF-8"))


def tokenize(x) -> tuple:
    import re
    subber = re.compile("[^a-zA-Z0-9-]")
    splitter = re.compile("\\s+")

    token_map = {}
    for i, s in enumerate(x):
        s = subber.sub(" ", s.lower())
        tokens = splitter.split(s)
        for tok in tokens:
            if tok == "":
                continue
            if tok not in token_map:
                token_map[tok] = []
            token_map[tok].append(i)

    all_tokens = sorted(list(token_map.keys()))
    all_indices = []
    for tok in all_tokens:
        all_indices.append(sorted(list(set(token_map[tok]))))

    return all_tokens, all_indices
