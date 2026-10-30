import os

from ._lib_gesel import validate_database_files as validate


def validate_database_files(
    path: str,
    species: str,
    num_genes: int
) -> None:
    """
    Validate Gesel database files against the `specification <https://github.com/gesel-inc/gesel-spec>`_.
    Invalid formatting will cause an error to be raised.

    Args:
        path:
            Path to a directory containing the database files.

        species:
            NCBI taxonomy ID of the species of interest.

        num_genes:
            Total number of genes available for this species.
            This can be obtained as the return value of :py:func:`~gesel.validate_gene_files`.

    Returns:
        ``None``.

    """
    validate(os.path.join(path, species + "_"), num_genes)
