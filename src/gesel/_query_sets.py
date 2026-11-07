from typing import Optional
import biocframe
import biocutils
import itertools

from ._search_genes import search_genes
from ._search_overlapping_sets import search_overlapping_sets
from ._search_set_text import search_set_text
from ._rename_genes_in_sets import _rename_genes_in_sets
from ._fetch_some_sets import fetch_some_sets
from ._fetch_some_collections import fetch_some_collections


def query_sets(
    species: str,
    genes: Optional[list] = None,
    text: Optional[str] = None,
    types: Optional[list] = None,
    counts_only: bool = True,
    config: Optional[dict] = None
) ->  biocframe.BiocFrame:
    """
    Query gene sets based on overlaps with genes of interest or matches to keyboards in their names/descriptions.
    This is a user-friendly wrapper for quick and convenient searching of the Gesel database;
    developers may prefer to use lower-level functions for more customization and flexibility.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        genes:
            List of gene identifiers of any supported type.
            These are typically Ensembl/Entrez identifiers or gene symbols.
            If provided, this function will search for gene sets that overlap any of the supplied genes.

        text:
            One or more keywords with which to search on, see the ``query`` argument in :py:func:`~gesel.search_set_text`.
            If provided, this function will search for gene sets that contain the (tokenized) keywords in their names or descriptions.

        types:
            Types of gene identifiers to consider for ``genes``.
            This should contain one or more of any type listed in :py:func:`~gesel.fetch_gene_types`.
            If ``None``, it defaults to all available types in :py:func:`~gesel.fetch_gene_types`.

        counts_only:
            Whether to return a list of the overlapping genes in each set.
            Only used if ``genes`` is provided.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:        
        A :py:class:`~biocframe.BiocFrame` containing one row per set that matches the query conditions.
        This contains the following columns:

        - ``name``, string containing the name of the gene set.
        - ``description``, string containing a description of the gene set.
        - ``size``, integer specifying the number of genes in this gene set.
        - ``collection``, the name of the collection that contains this gene set.
        - ``set``, integer specifying the Gesel set index that can be used in other functions like :py:func:`~gesel.fetch_genes_for_some_sets`.

        If ``genes`` is provided, the data frame will additionally contain:

        - ``count``, integer containing the number of overlaps between the genes in the set and those in ``genes``.
        - ``which``, a nested list where each entry is a character vector containing the genes in ``genes`` that are present in each set.
          Only reported if ``counts_only = False``.
        - ``pvalue``, a numeric column containing the hypergeometric p-value for overrepresentation of ``genes`` in eachset.
          Rows will be sorted by this column if it is present.

    Examples:
        >>> import gesel
        >>> out = gesel.query_sets(
        >>>     species = "9606",
        >>>     genes = ["tead1", "tead2", "tead3", "tead4"],
        >>>     text = "transcription"
        >>> )
        >>> print(out)
        >>>
        >>> out2 = gesel.query_sets(
        >>>     species = "9606",
        >>>     genes = ["SNAP25", "neurod4", "neurod6"],
        >>>     text = "neuro*",
        >>>     counts_only = False 
        >>> )
        >>> print(out2)
    """

    if genes is not None:
        mapped = search_genes(species, genes, types = types, config = config)
        output = search_overlapping_sets(species, genes = itertools.chain(*mapped), counts_only = counts_only, config = config)
        output = output.remove_column("size") # this will be added by fetchSomeSets, no need for it here.
        output = output[biocutils.order(output.get_column("pvalue")),:]

        if not counts_only:
            # Converting it back to the user-provided identifiers.
            # This is more intuitive than using some arbitrarily chosen identifier from the gene files.
            n = 0
            for curm in mapped:
                for i in curm:
                    n = max(n, i + 1)
            revmap = []
            for i in range(n):
                revmap.append([])
            for g, curm in enumerate(mapped):
                for i in curm:
                    revmap[i].append(genes[g])
            output = output.set_column("which", _rename_genes_in_sets(revmap, output.get_column("which")))
    else:
        output = None

    if text is not None:
        tout = search_set_text(species, text, config = config)
        if output is not None:
            to_keep = set(tout)
            to_keep_idx = []
            for i, s in enumerate(output.get_column("set")):
                if s in to_keep:
                    to_keep_idx.append(i)
            output = output[to_keep_idx,:]
        else:
            output = biocframe.BiocFrame({ "set": tout })

    if output is None:
        raise ValueError("at least one of 'genes' or 'text' must be provided")

    details = fetch_some_sets(species, output.get_column("set"), config = config)
    output = details.combine_columns(output)
    output = output.set_column("collection", fetch_some_collections(species, output.get_column("collection"), config = config)["title"])
    output = output.remove_column("number")
    return output

