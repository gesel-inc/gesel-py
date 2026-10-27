# Changelog

## Version 0.1.1

- Switched to the new feedstock repository at https://github.com/gesel-inc/feedstock in `database_url()` and `gene_url()`.
- Added `fetch_gene_types()` and `fetch_gene_version()` to get the available gene identifier types and version.
- Updated `fetch_all_genes()` to set `types = None` to default to all available gene identifier types.

## Version 0.1.0

- First release of the **gesel** client package.
