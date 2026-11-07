from typing import Optional

from ._fetch_all_genes import fetch_all_genes


def _rename_genes_in_sets(gene_ids: dict, sets: list) -> list:
    output = []
    for curset in sets:
        present = set()
        collected = []
        for g in curset:
            for nm in gene_ids[g]:
                if nm in present:
                    continue
                collected.append(nm) # making sure we add things in order.
                present.add(nm)
        output.append(collected)
    return output 


def rename_genes_in_sets(species: str, sets: list, type: str, config: Optional[dict] = None) -> list:
    """
    Convert genes in sets from row indices to their identifiers.
    If a gene has no identifiers of the specified ``type``, it is omitted from the affected character vectors in the output list.
    If a gene has multiple identifiers of the specified ``type``, all identifiers are reported in the affected character vectors in the output list.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        sets:
            List of lists, typically returned by :py:func:`~gesel.fetch_genes_for_some_sets` or :py:func:`~gesel.fetch_genes_for_all_sets`.
            Each inner list represents a gene set and contains the identities of the genes (as row indices) in that set.

        type:
            Type of gene identifier to convert to.
            This can be any type listed in :py:func:`~gesel.fetch_gene_types`.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        List of lists of strings.
        Each inner list represents a gene set and contains the identifies of the genes (as the specified ``type``) in that set.

    Examples:
        >>> import gesel
        >>> sets = gesel.fetch_genes_for_some_sets("9606", range(0, 5))
        >>> gesel.rename_genes_in_sets("9606", sets, "symbol")
    """
    all_genes = fetch_all_genes(species, [type], config = config)[type]
    return _rename_genes_in_sets(all_genes, sets)
