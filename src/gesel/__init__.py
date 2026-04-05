import sys

if sys.version_info[:2] >= (3, 8):
    # TODO: Import directly (no need for conditional) when `python_requires = >= 3.8`
    from importlib.metadata import PackageNotFoundError, version  # pragma: no cover
else:
    from importlib_metadata import PackageNotFoundError, version  # pragma: no cover

try:
    # Change here if project is renamed and does not equal the package name
    dist_name = __name__
    __version__ = version(dist_name)
except PackageNotFoundError:  # pragma: no cover
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError


from ._download_database_file import download_database_file, database_url
from ._download_database_ranges import download_database_ranges, download_multipart_ranges
from ._download_gene_file import download_gene_file, gene_url

from ._fetch_all_collections import fetch_all_collections
from ._fetch_all_genes import fetch_all_genes
from ._fetch_all_sets import fetch_all_sets
from ._fetch_some_sets import fetch_some_sets, fetch_set_sizes
from ._fetch_some_collections import fetch_some_collections, fetch_collection_sizes

from ._fetch_genes_for_all_sets import fetch_genes_for_all_sets
from ._fetch_sets_for_all_genes import fetch_sets_for_all_genes
from ._fetch_genes_for_some_sets import fetch_genes_for_some_sets
from ._fetch_sets_for_some_genes import fetch_sets_for_some_genes, effective_number_of_genes
from ._find_overlapping_sets import find_overlapping_sets

from ._map_genes_by_name import map_genes_by_name
from ._search_genes import search_genes
from ._search_set_text import search_set_text

from ._new_config import new_config, flush_memory_cache


__all__ = []
_toignore = set(["sys", "biocutils", "biocframe"]) 
for _name in dir():
    if _name.startswith("_") or _name in _toignore:
        continue
    __all__.append(_name)
