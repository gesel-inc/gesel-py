def validate_gene_files(
    path: str,
    species: str,
    types: list = None
) -> int:
    """
    Validate Gesel gene annotation files against `the specification <https://github.com/gesel-inc/gesel-spec>`_.
    Invalid formatting will cause an error to be raised.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        path:
            Path to a directory containing the gene annotation files.

        types:
            List of gene identifier types to validate, e.g., ``symbol``, ``ensembl``.
            If ``None``, all detected files for ``species`` in ``path`` are checked.

    Returns:
        Number of genes, to be used as ``num_genes`` in :py:func:`~gesel.validate_database_files`.
    """
    # Currently disabled!
    return 0
