from typing import Optional
import biocutils

from . import _new_config as cfg
from . import _utils as utils


def search_set_text(
    species: str,
    query: str,
    use_name: bool = True,
    use_description: bool = True,
    config: Optional[dict] = None 
) -> list:
    """
    Search for sets based on their names and descriptions.

    Args:
        species:
            NCBI taxonomy ID of the species of interest.

        query:
            One or more words to search on.
            A set is only matched if it matches to all of the tokens in the query in its name/description.
            The ``*`` and ``?`` wildcards can be used to match to any or one character, respectively.

        genes:
            List of integers containing the gene indices.
            Each gene index refers to a row of the data frame returned by :py:func:`~gesel.fetch_all_genes`.

        use_name:
            Whether to search for the query string in the name of the set.

        use_description:
            Whether to search for the query string in the description of the set.

        config:
            Configuration object, typically created by :py:func:`~gesel.new_config`.
            If ``None``, the default configuration is used.

    Returns:
        List of set indices for the matching gene sets.
        Each set index refers to a row in the data frame returned by :py:func:`~gesel.fetch_all_sets`.

    Examples:
        >>> import gesel
        >>> out = gesel.search_set_text("9606", "cancer")
        >>> print(gesel.fetch_all_sets("9606")[out, :])
        >>>
        >>> out = gesel.search_set_text("9606", "innate immun*")
        >>> print(gesel.fetch_all_sets("9606")[out, :])
    """

    import re
    matcher = re.compile("[^a-zA-Z0-9?*-]")
    tokens = set()
    for tok in matcher.split(query.lower()):
        tok = tok.encode("utf-8") # everything is a bytestring for consistency with the internal representation.
        if tok != b"" and tok != b"-":
            tokens.add(tok)
    tokens = list(tokens)

    config = cfg._get_config(config)
    if use_name:
        gathered_names = _fetch_sets_by_token(config, species, tokens, "names")
    if use_description:
        gathered_descriptions = _fetch_sets_by_token(config, species, tokens, "descriptions")

    if use_name and use_description:
        gathered = []
        for i in range(len(tokens)):
            gathered.append(gathered_names[i] + gathered_descriptions[i])
    elif use_name:
        gathered = gathered_names
    elif use_description:
        gathered = gathered_descriptions
    else:
        return []

    return biocutils.intersect(*gathered)


def _fetch_sets_by_token(
    config: dict,
    species: str,
    tokens: list,
    type: str
) -> list:
    cached = cfg._get_cache(config, "search_set_text", species)
    modified = False

    if cached is None:
        cached = {}
        modified = True

    fname = species + "_tokens-" + type + ".tsv"
    if type in cached:
        tfound = cached[type]
    else:
        tfound = {}
        names, ranges = cfg._retrieve_ranges_with_names(config, fname)
        tfound["ranges"] = ranges
        tfound["names"] = names
        tfound["prior"] = {}
        modified = True

    tnames = tfound["names"]
    prior = tfound["prior"]

    # Finding the unique set of all tokens that haven't been resolved yet.
    to_request = set()
    partial_request = {}

    for tok in tokens:
        if tok in prior:
            continue

        has_qm = tok.find(b"?")
        has_star = tok.find(b"*")

        if has_qm == 0 or has_star == 0:
            # No choice but to do a full scan if we start with a wildcard.
            matcher = _create_wildcard_regex(tok)
            collected = []
            for idx, curname in enumerate(tnames):
                if matcher.match(curname):
                    collected.append(curname)
                    to_request.add(idx)
            partial_request[tok] = collected

        elif has_qm > 0 or has_star > 0:
            if has_qm > 0 and has_star > 0: 
                prefix = tok[:min(has_qm, has_star)]
            elif has_qm > 0:
                prefix = tok[:has_qm]
            else:
                prefix = tok[:has_star]

            # We can use a binary search on the pre-wildcard prefix.
            import bisect
            idx = bisect.bisect_left(tnames, prefix)
            matcher = _create_wildcard_regex(tok)

            collected = []
            while idx < len(tnames):
                curname = tnames[idx] 
                if matcher.match(curname):
                    collected.append(curname)
                    to_request.add(idx)
                elif not curname.startswith(prefix):
                    break
                idx += 1
            partial_request[tok] = collected

        else:
            # We can use a binary search.
            import bisect
            idx = bisect.bisect_left(tnames, tok)
            if idx < len(tnames):
                if tnames[idx] == tok:
                    to_request.add(idx)

    # Requesting ranges for anything that we're missing.
    to_request = list(to_request)
    if len(to_request) > 0:
        ranges = tfound["ranges"]
        starts = []
        ends = []
        for r in to_request:
            starts.append(ranges[r])
            ends.append(ranges[r + 1])

        deets = cfg._fetch_ranges(config, fname, starts, ends)
        for i, r in enumerate(to_request):
            prior[tnames[r]] = utils._decode_indices(deets[i])
        modified = True

    # Filling up the caches for subsequent queries.
    for needed_token, actual_tokens in partial_request.items():
        to_add = []
        for tok in actual_tokens:
            to_add += prior[tok]
        prior[needed_token] = to_add
        modified = True

    if modified:
        tfound["prior"] = prior
        cached[type] = tfound
        cfg._set_cache(config, "search_set_text", species, cached)

    output = []
    for tok in tokens:
        output.append(prior[tok])
    return output


def _create_wildcard_regex(token: str):
    # Easier to assemble it as a string and then convert it back to a bytestring.
    # No need to set '^' as we use re.match to match only the start of the string.
    new_pattern = "" 
    for x in token.decode("utf-8"):
        if x == "?":
            new_pattern += "."
        elif x == "*":
            new_pattern += ".*"
        else:
            new_pattern += x
    new_pattern += "$"
    import re
    return re.compile(new_pattern.encode("utf-8"))
