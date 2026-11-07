from typing import Optional
import biocutils

from ._fetch_genes_for_all_sets import fetch_genes_for_all_sets
from ._rename_genes_in_sets import rename_genes_in_sets
from ._fetch_all_sets import fetch_all_sets
from ._fetch_all_collections import fetch_all_collections


def load_all_sets(
    species: str,
    type: str,
    config: Optional[dict] = None,
    as_compressed: bool = False
) -> tuple:
    """
    Load information about all gene sets for a species.
    This includes its gene membership as well as details like its name and description.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        type:
            Type of gene identifier to convert to.
            This can be any type listed in :py:func:`~gesel.fetch_gene_types`.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

        as_compressed:
            Whether to return a :py:class:`~compressed_lists.CompressedCharacterList`.
            This assumes that the **compressed_lists** package is installed.

    Returns:
        If ``as_compressed = False``, a tuple is returned consisting of:
        
        1. ``sets``, a :py:class:`~biocutils.NamedList` of length equal to the total number of sets for ``species``.
           Each list element is a nested list that corresponds to a gene set and contains the genes in that set.
           Each gene is represented by zero, one or more identifiers of the specified ``type`` (see :py:func:`~gesel.rename_genes_in_sets` for details).
           The positional index of each set in ``sets`` can be used as the Gesel set index in other functions like :py:class:`~gesel.fetch_genes_for_some_sets`.
           Each list element is named according to its set, i.e., the ``name`` column of ``details``.
        2. ``details``, a :py:class:`~biocframe.BiocFrame` where each row corresponds to a gene set in ``sets``.
           This contains the following columns:

           - ``name``, string containing the name of the gene set.
           - ``description``, string containing a description of the gene set.
           - ``size``, integer specifying the number of genes in this gene set.
             Note that this may not equal the length of the corresponding entry of ``sets``,
             if any gene does not have exactly one identifier of the specified ``type``. 
           - ``collection``, the name of the collection that contains this gene set.

           The row index of each set in ``details`` can be used as the Gesel set index in functions like :py:class:`~gesel.fetch_genes_for_some_sets`.

        If ``as_compressed = True``, a :py:class:`~compressed_lists.CompressedList` of length equal to the total number of sets for ``species`` is returned.
        Each list element is a nested list that contains the identifiers of genes in that set, as described above for ``sets``.
        The element metadata contains more details about each set as described above for ``details``.

    Examples:
        >>> import gesel
        >>> sets, details = gesel.load_all_sets("7227", "symbol")
        >>> sets[:5]
        >>> print(details)
        >>>
        >>> everything2 = gesel.load_all_sets("7227", "symbol", as_compressed = True)
        >>> print(everything2)
        >>> print(everything2.get_element_metadata())
    """

    all_sets = fetch_genes_for_all_sets(species, config = config)
    all_sets = rename_genes_in_sets(species, all_sets, type, config = config)
    all_sets = biocutils.NamedList(all_sets)

    details = fetch_all_sets(species, config = config)
    coltitles = biocutils.subset(fetch_all_collections(species, config = config)["title"], details.get_column("collection"))
    details = details.set_column("collection", coltitles)
    details = details.remove_column("number")
    all_sets.set_names(details.get_column("name"), in_place=True)

    if as_compressed:
        import compressed_lists
        output = compressed_lists.CompressedList.from_list(all_sets)
        output.set_element_metadata(details, in_place=True)
        return output
    else:
        return all_sets, details
