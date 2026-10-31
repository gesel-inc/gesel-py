from typing import Optional
import biocutils
import biocframe

from ._fetch_sets_for_some_genes import fetch_sets_for_some_genes, effective_number_of_genes
from ._fetch_some_sets import fetch_set_sizes
from ._lib_gesel import compute_enrichment


def search_overlapping_sets(
    species: str,
    genes: list,
    counts_only: bool = True,
    test_enrichment: bool = True,
    config: Optional[dict] = None
) -> biocframe.BiocFrame:
    """
    Find all sets overlapping any gene in a user-supplied list, and return the number of overlaps per set.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        genes:
            List of integers containing gene indices.
            Each gene index refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_genes`.

        counts_only:
            Whether to only report the number of overlapping genes for each set.

        test_enrichment:
            Whether to compute a hypergeometric p-value for enrichment of ``genes`` in each set.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        A :py:class:`~biocframe.BiocFrame` where each row represents a set.
        It contains the following columns: 

        - ``set``,  the identity of the set corresponding to each row.
          This set index refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_sets`.
        - ``counts``, the number of overlaps between the genes in the set and those in ``genes``.
        - ``which``, if ``counts_only = False``.
          This contains the entries of ``genes`` that overlap with those in the set.
        - ``size``, if ``test_enrichment = True``.
          This contains the size of the set.
        - ``pvalue``, if ``test_enrichment = True``.
          This contains the hypergeometric p-value for overrepresentation of ``genes`` in the set.

        The row order is arbitrary.

        If ``test_enrichment = True``, the :py:class:`~biocframe.BiocFrame` will also contain a ``present`` integer in its metadata.
        This is the number of genes in ``genes`` that are present in at least one set in the Gesel database for ``species``.
        The value of ``present`` is intended for use as the number of draws when performing a hypergeomtric test for gene set enrichment, instead of ``len(genes)``.
        It ensures that genes outside of the Gesel universe are ignored, e.g., due to user error, different genome versions.
        Otherwise, unknown genes would inappropriately increase the number of draws and inflate the enrichment p-value.

    Examples:
        >>> # Pretend we're interested in the first 10 genes. 
        >>> genes_of_interest = range(10)
        >>>
        >>> import gesel
        >>> overlaps = gesel.search_overlapping_sets("9606", genes_of_interest)
        >>> print(overlaps)
        >>>
        >>> # More details on the overlapping sets.
        >>> all_sets = gesel.fetch_all_sets("9606")
        >>> print(all_sets[overlaps["set"],:])
    """

    genes = list(set(genes))
    info = fetch_sets_for_some_genes(species, genes, config)

    if counts_only:
        collected = {}
        for sets in info:
            for s in sets:
                if s in collected:
                    collected[s] += 1
                else:
                    collected[s] = 1

        sets = []
        counts = []
        for s, count in collected.items():
            sets.append(s)
            counts.append(count)

        overlap = biocframe.BiocFrame({
            "set": sets,
            "count": counts
        })

    else:
        collected = {}
        for g, sets in enumerate(info):
            gid = genes[g]
            for s in sets:
                if s in collected:
                    collected[s].append(gid)
                else:
                    collected[s] = [gid]

        sets = []
        counts = []
        members = []
        for s, genes in collected.items():
            sets.append(s)
            members.append(genes)
            counts.append(len(genes))

        overlap = biocframe.BiocFrame({
            "set": sets,
            "count": counts,
            "which": members
        })

    if test_enrichment:
        present = 0
        for sets in info:
            present += len(sets) > 0
        overlap.set_metadata({ "present": present }, in_place = True)

        set_sizes = biocutils.subset(fetch_set_sizes(species, config = config), overlap.get_column("set"))
        overlap.set_column("size", set_sizes, in_place = True)

        universe = effective_number_of_genes(species, config = config)
        pvalue = compute_enrichment(
            overlap.get_column("count"),
            overlap.get_column("size"),
            universe, 
            present
        )
        overlap.set_column("pvalue", pvalue, in_place = True)

    return overlap


def find_overlapping_sets(*args, **kwargs):
    """Deprecated, use :py:func:`~search_overlapping_sets` instead."""
    out = search_overlapping_sets(*args, **kwargs)
    cn = out.get_column_names()
    if "which" in cn:
        cn[cn.as_list().index("which")] = "genes"
        out.set_column_names(cn, in_place=True)
    return out, out.get_metadata()["present"]
