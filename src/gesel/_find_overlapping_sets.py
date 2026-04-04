from typing import Optional
import biocutils
import biocframe

from ._fetch_sets_for_some_genes import fetch_sets_for_some_genes


def find_overlapping_sets(
    species: str,
    genes: list,
    counts_only: bool = True,
    config: Optional[dict] = None
) -> tuple:
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

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        A tuple of length 2.

        The first element is a :py:class:`~biocframe.BiocFrame` describing the overlapping sets.
        Each row represents a set that is identified by the set index in the ``set`` column.
        (This set index refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_sets`.)
        It also has:

        - The ``counts`` column, if ``counts_only = True``.
          This specifies the number of overlaps between the genes in the set and those in ``genes``.
        - The ``genes`` column, if ``counts_only = False``.
          This is a list that contains the entries of ``genes`` that overlap with those in the set.

        Rows are sorted by the number of overlapping genes, in decreasing order.

        The second element is an integer scalar containing the number of genes in ``genes`` that are present in at least one set in the Gesel database for ``species``.
        This is intended for use as the number of draws when performing a hypergeomtric test for gene set enrichment, instead of ``len(genes)``.
        It ensures that genes outside of the Gesel universe are ignored, e.g., due to user error, different genome versions.
        Otherwise, unknown genes would inappropriately increase the number of draws and inflate the enrichment p-value.

    Examples:
        >>> # Present like the first 10 genes are what we're interested in.
        >>> genes_of_interest = range(10)
        >>>
        >>> import gesel
        >>> overlaps, present = gesel.find_overlapping_sets("9606", genes_of_interest)
        >>> print(overlaps)
        >>> present
        >>>
        >>> # More details on the overlapping sets.
        >>> all_sets = gesel.fetch_all_sets("9606")
        >>> print(all_sets[overlaps["set"],:])
    """

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
        o = biocutils.order(counts, decreasing=True)

        overlap = biocframe.BiocFrame({
            "set": biocutils.subset(sets, o),
            "count": biocutils.subset(counts, o)
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
        o = biocutils.order(counts, decreasing=True)

        overlap = biocframe.BiocFrame({
            "set": biocutils.subset(sets, o),
            "genes": biocutils.subset(members, o)
        })

    present = 0
    for sets in info:
        present += len(sets) > 0

    return overlap, present
