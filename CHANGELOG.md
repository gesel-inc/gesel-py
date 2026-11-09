# Changelog

## Version 0.2.0

- Consolidate multiple range requests into blocks to reduce network traffic and improve caching in all `*_some_*()` functions.
  The block size can be set via `consolidate_block_size()` or the `consolidate_block_size=` argument in `new_config()`.
- Relaxed the requirements for the `fetch_ranges=` function in `new_config()` to support coalesced ranges in the output.
- Implement `load_all_sets()`, `rename_genes_in_sets()` and `query_sets()` for more user-friendly interactions with the Gesel database.
- Renamed `map_genes_by_name()` to `create_gene_identifier_map()` for consistency with the R package.
- Implement `read_database_ranges()` to allow fetching of ranges from a local file.
- Set `types=None` as the default in `search_genes()` to use all available gene types.
- Wrap the **gesel** C++ library to support validation of database and gene annotation files in the `validate_*_files()` functions.
- Renamed `find_overlapping_sets()` to `search_overlapping_sets()` for consistency with the R package.
  The new function now computes hypergeometric p-values to test for enrichment.
  It also returns a BiocFrame directly rather than a tuple, given that the ``present`` option is not particularly relevant to most users.

## Version 0.1.1

- Switched to the new feedstock repository at https://github.com/gesel-inc/feedstock in `database_url()` and `gene_url()`.
- Added `fetch_gene_types()` and `fetch_gene_version()` to get the available gene identifier types and version.
- Updated `fetch_all_genes()` to set `types = None` to default to all available gene identifier types.

## Version 0.1.0

- First release of the **gesel** client package.
