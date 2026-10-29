from typing import Optional, Literal
import biocframe
import os

from ._validate_gene_files import validate_gene_files


def prepare_gene_files(
    species: str,
    genes: dict,
    path: str = ".",
    validate: bool = True,
    version: Literal["0.2.0", "0.1.0"] = "0.2.0"
) -> None:
    """
    Prepare Gesel gene annotation files containing the gene identifiers.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        genes:
            Dictionary of lists.
            Each list corresponds to an identifier type and is named accordingly, e.g., ``genes["ensembl"]`` for Ensembl.
            Each list should be of length equal to the total number of genes.
            Each entry of the list corresponds to a gene and is a nested list of strings containing identifiers of the specified type for that gene,
            e.g., ``genes["ensembl"][10]`` contains a list of Ensembl IDs for the 9th gene.
            The nested list may be empty if no identifiers are available for a gene.

            Alternatively, a :py:class:`~biocframe.BiocFrame` where each row corresponds to a gene and each column is a list of nested lists of identifiers as described above,
            see the output of :py:func:`~gesel.fetch_all_genes` for details.

        path:
            Path to a directory in which to create the gene annotation files.

        validate:
            Whether to run :py:func:`~gesel.validate_gene_files` on the newly created files.

        version:
            Version of the Gesel gene annotation file specification to use for saving ``genes``.

    Returns:
        Several files are produced inside ``path`` with the ``species_`` prefix.
        ``None`` is returned.

    Examples:
        >>> import gesel
        >>> genes = {
        ...     "ensembl": [["ENSG1"], ["ENSG2", "ENSG3"], [], ["ENSG4"]],
        ...     "entrez": [["1"], [], ["2", "3", "4"], ["5", "6"]],
        ...     "foobar": [["malat1"], ["neat1"], ["Gm1234"], ["LINC0000001"]]
        ... }
        >>>
        >>> import tempfile
        >>> tmp = tempfile.mkdtemp()
        >>> gesel.prepare_gene_files("1234", genes, tmp)
        >>>
        >>> import os
        >>> config = gesel.new_config(fetch_gene = lambda x : os.path.join(tmp, x))
        >>> print(gesel.fetch_all_genes("1234", config = config))
    """

    if isinstance(genes, biocframe.BiocFrame):
        genes = genes.to_dict()

    if version == "0.1.0":
        sep = "_"
        to_validate = list(genes.keys()) # validation can't be trusted to auto-determine types if we mix it with the database files.
    else:
        with open(os.path.join(path, species + "_gene-types.tsv"), "wb") as handle:
            for gene_type in genes.keys():
                handle.write((gene_type + '\n').encode("UTF-8"))
        with open(os.path.join(path, species + "_gene-version.tsv"), "wb") as handle:
            handle.write((version + '\n').encode("UTF-8"))
        sep = "_gene-type-"
        to_validate = None # validation will automatically determine types from the manifest.

    import gzip
    for gene_type, gene_aliases in genes.items():
        with gzip.open(os.path.join(path, species + sep + gene_type + ".tsv.gz"), "wb") as handle:
            for gene in gene_aliases:
                handle.write(('\t'.join(gene) + '\n').encode("UTF-8"))

    if validate:
        validate_gene_files(path, species, types = to_validate)
