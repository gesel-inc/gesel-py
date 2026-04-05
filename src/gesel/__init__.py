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

from ._download_database_file import *
from ._download_database_ranges import *
from ._download_gene_file import *

from ._fetch_all_collections import *
from ._fetch_all_genes import *
from ._fetch_all_sets import *

from ._fetch_some_sets import *
from ._fetch_some_collections import *

from ._fetch_genes_for_all_sets import *
from ._fetch_sets_for_all_genes import *
from ._fetch_genes_for_some_sets import *
from ._fetch_sets_for_some_genes import *
from ._find_overlapping_sets import *

from ._map_genes_by_name import *
from ._search_genes import *

from ._new_config import *
