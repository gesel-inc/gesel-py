from typing import Optional
import biocutils

from . import _new_config as cfg
from . import _utils as utils


def fetch_sets_for_some_genes(species: str, genes: list, config: Optional[dict] = None) -> list:
    """
    Fetch all sets that contain some genes in the Gesel database.
    This can be more efficient than :py:func:`~gesel.fetch_sets_for_all_genes` if only a few genes are of interest.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        genes:
            List of integers containing the gene indices.
            Each gene index refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_genes`.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        List of integer vectors.
        Each vector corresponds to a gene in ``genes`` and contains the identities of the sets containing that gene.
        Each set is defined by its set index, which refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_sets`.

    Examples:
        >>> import gesel
        >>> has_genes = gesel.fetch_sets_for_some_genes("9606", [0, 5, 10])
        >>> has_genes[0]
        >>>
        >>> # Sets containing the first gene:
        >>> set_info = gesel.fetch_all_sets("9606")
        >>> print(set_info[has_genes[0], :])
        >>>
        >>> # Identities of the genes used above:
        >>> gene_symbols = gesel.fetch_all_genes("9606")["symbol"]
        >>> import biocutils
        >>> print(biocutils.subset(gene_symbols, [0, 5, 10]))
    """

    config = cfg.get_config(config)
    candidate = cfg.get_cache(config, "fetch_sets_for_all_genes", species)
    if candidate is not None:
        return biocutils.subset(candidate, genes)

    fname = species + "_gene2set.tsv"
    cached, modified = _get_sets_for_some_genes_ranges(config, species, fname)
    prior_gene = cached["prior"]["gene"]
    prior_sets = cached["prior"]["sets"]

    # TODO: move this to biocutils as setdiff().
    needed = []
    already_present = set(prior_gene)
    for g in genes:
        if g not in already_present:
            needed.append(g)

    if len(needed) > 0:
        intervals = cached["intervals"]
        starts = []
        ends = []
        for g in needed:
            starts.append(intervals[g])
            ends.append(intervals[g + 1])
        deets = cfg.fetch_ranges(config, fname, starts, ends)
        for line in deets:
            prior_sets.append(utils._decode_indices(line))
        prior_gene += needed
        modified = True

    if modified:
        cached["prior"]["gene"] = prior_gene
        cached["prior"]["sets"] = prior_sets
        cfg.set_cache(config, "fetch_sets_for_some_genes", species, cached)

    m = biocutils.match(genes, prior_gene)
    return biocutils.subset(prior_sets, m)


def _get_sets_for_some_genes_ranges(config: dict, species: str, fname: str) -> tuple:
    cached = cfg.get_cache(config, "fetch_sets_for_some_genes", species)
    if cached is not None:
        return cached, False

    intervals = cfg._retrieve_ranges(config, fname)
    cached = {
        "intervals": intervals,
        "prior": {
            "gene": [],
            "sets": []
        }
    }
    return cached, True


#' Effective number of genes
#'
#' Count the number of genes in the Gesel database that belong to at least one set.
#'
#' @inheritParams fetchAllCollections
#'
#' @details
#' The return value should be used as the total number of balls when performing a hypergeometric test for gene set enrichment
#' (see \code{\link{phyper}}), instead of \code{nrow(fetchAllGenes(species))}.
#' This ensures that uninteresting genes like pseudo-genes or predicted genes are ignored during the calculation.
#' Otherwise, unknown genes would inappropriately increase the number of balls and understate the enrichment p-values. 
#'
#' @return Integer scalar specifying the number of genes in Gesel that belong to at least one set.
#'
#' @author Aaron Lun
#'
#' @export

def effective_number_of_genes(species: str, config: Optional[dict] = None) -> int:
    config = cfg.get_config(config)
    candidate = cfg.get_cache(config, "fetch_sets_for_all_genes", species)
    if candidate is not None:
        number = 0
        for can in candidate:
            number += len(can) > 0
        return number

    fname  = species + "_gene2set.tsv"
    cached, modified = _get_sets_for_some_genes_ranges(config, species, fname)
    if modified:
        cfg.set_cache(config, "fetch_sets_for_some_genes", species, cached)

    intervals = cached["intervals"]
    number = 0
    for i in range(1, len(intervals)):
        number += (intervals[i] - intervals[i-1] > 1) # account for the newline character
    return number
