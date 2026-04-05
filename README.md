[![PyPI-Server](https://img.shields.io/pypi/v/gesel.svg)](https://pypi.org/project/gesel/)
![Unit tests](https://github.com/gesel-inc/gesel-py/actions/workflows/run-tests.yml/badge.svg)

# Gene set selections in Python

## Overview

The **gesel** package provides a Python interface to the [Gesel database](https://github.com/gesel-inc/gesel-spec) for client-side gene set searches.
The idea is to use HTTP range requests to serve the gene-to-set mappings to a client without downloading the entire database or implementing custom server logic.
In this manner, we can execute a variety of interesting gene set queries with high scalability across users and minimal backend maintenance.

## Quick start

To get started, install the package from [PyPI](https://pypi.org/project/gesel/):

```bash
pip install gesel
```

Then we can find overlaps between our genes of interest and the gene sets in the Gesel database.
(Note that the exact numbers are subject to change, pending updates to the version of the Gesel database.)

```python
import gesel
my_genes = ["SNAP25", "NEUROD6", "GAD1", "GAD2", "RELN"]

# First, mapping our gene names to Gesel's internal gene indices.
gene_idx = gesel.search_genes("9606", my_genes) # list of lists of gene indices.
print(gene_idx)
## [[4639], [12767], [1758], [1759], [3912]]
gene_idx = sum(gene_idx, []) # collapsing it to a list of integers, for simplicity.
print(gesel.fetch_all_genes("9606")[gene_idx,:]) # double-checking that we got it right.
## BiocFrame with 5 rows and 3 columns
##          symbol    entrez             ensembl
##          <list>    <list>              <list>
## [0]  ['SNAP25']  ['6616'] ['ENSG00000132639']
## [1] ['NEUROD6'] ['63974'] ['ENSG00000164600']
## [2]    ['GAD1']  ['2571'] ['ENSG00000128683']
## [3]    ['GAD2']  ['2572'] ['ENSG00000136750']
## [4]    ['RELN']  ['5649'] ['ENSG00000189056']

# Now finding all sets with one or more overlaps to `my_genes`.
overlaps, present = gesel.find_overlapping_sets("9606", gene_idx, counts_only=False)
print(overlaps) # set index and the identities of overlapping genes.
## BiocFrame with 1163 rows and 2 columns
##           set                     genes
##        <list>                    <list>
##    [0]   2420  [4639, 1758, 1759, 3912]
##    [1]   2521  [4639, 1758, 1759, 3912]
##    [2]  21748 [4639, 12767, 1758, 1759]
##           ...                       ...
## [1160]  40562                    [3912]
## [1161]  40597                    [3912]
## [1162]  40599                    [3912]

# Actually getting the identities of the top sets:
set_info = gesel.fetch_some_sets("9606", overlaps["set"][:10])
print(set.info)
## BiocFrame with 10 rows and 5 columns
##                         name             description   size collection number
##                       <list>                  <list> <list>     <list> <list>
## [0]               GO:0005737               cytoplasm   5010          0   2420
## [1]               GO:0005886         plasma membrane   4778          0   2521
## [2]  BLALOCK_ALZHEIMERS_D... http://www.gsea-msig...   1248          2   2515
## [3]  MANNO_MIDBRAIN_NEURO... http://www.gsea-msig...   1106         14     92
## [4]               GO:0005515         protein binding  12505          0   2310
## [5]               GO:0007268 chemical synaptic tr...    248          0   3331
## [6]  MIKKELSEN_MEF_HCP_WI... http://www.gsea-msig...    591          2   1896
## [7]  REACTOME_NEUROTRANSM... http://www.gsea-msig...     51          4     29
## [8]  REACTOME_TRANSMISSIO... http://www.gsea-msig...    270          4     32
## [9] REACTOME_NEURONAL_SYSTEM http://www.gsea-msig...    411          4     33

# As well as the collections from which they were derived.
print(gesel.fetch_some_collections("9606", [0, 2, 4, 14]))
## BiocFrame with 4 rows and 6 columns
##                       title             description maintainer                  source  start   size
##                      <list>                  <list>     <list>                  <list> <list> <list>
## [0]           Gene ontology Gene sets defined fr...  Aaron Lun https://github.com/L...      0  18933
## [1] MSigDB chemical and ... Gene sets that repre...  Aaron Lun https://github.com/L...  19233   3405
## [2] MSigDB canonical pat... Reactome gene sets a...  Aaron Lun https://github.com/L...  22834   1654
## [3] MSigDB cell type sig... Gene sets that conta...  Aaron Lun https://github.com/L...  39774    830
```

Check out the [reference documentation](https://gesel-inc.github.io/gesel-py) for more details.

## Searching on text

We can also search for gene sets based on the text in their names or descriptions.

```python
chits = gesel.search_set_text("9606", "cancer")
print(gesel.fetch_some_sets("9606", chits[:10]))
## BiocFrame with 10 rows and 5 columns
##                        name             description   size collection number
##                      <list>                  <list> <list>     <list> <list>
## [0] SOGA_COLORECTAL_CANC... http://www.gsea-msig...     71          2      1
## [1] SOGA_COLORECTAL_CANC... http://www.gsea-msig...     82          2      2
## [2] WATANABE_RECTAL_CANC... http://www.gsea-msig...    113          2     64
## [3]  LIU_PROSTATE_CANCER_UP http://www.gsea-msig...     99          2     66
## [4] BERTUCCI_MEDULLARY_V... http://www.gsea-msig...    207          2     68
## [5] WATANABE_COLON_CANCE... http://www.gsea-msig...     29          2     78
## [6] WATANABE_COLON_CANCE... http://www.gsea-msig...     69          2     79
## [7] SOTIRIOU_BREAST_CANC... http://www.gsea-msig...     53          2     81
## [8] CHARAFE_BREAST_CANCE... http://www.gsea-msig...     52          2    124
## [9] DOANE_BREAST_CANCER_... http://www.gsea-msig...     33          2    125

ihits = gesel.search_set_text("9606", "innate immun*")
print(gesel.fetch_some_sets("9606", ihits[:10]))
## BiocFrame with 10 rows and 5 columns
##                        name             description   size collection number
##                      <list>                  <list> <list>     <list> <list>
## [0] REACTOME_INNATE_IMMU... http://www.gsea-msig...   1118          4    229
## [1] REACTOME_REGULATION_... http://www.gsea-msig...     15          4    552
## [2] REACTOME_SARS_COV_1_... http://www.gsea-msig...     41          4   1562
## [3] REACTOME_SARS_COV_2_... http://www.gsea-msig...    126          4   1580
## [4] WP_SARSCOV2_B117_VAR... http://www.gsea-msig...      9          5    185
## [5] WP_SARS_CORONAVIRUS_... http://www.gsea-msig...     31          5    189
## [6] WP_SARSCOV2_INNATE_I... http://www.gsea-msig...     66          5    318
## [7] WP_PATHWAYS_OF_NUCLE... http://www.gsea-msig...     16          5    729
## [8]              GO:0002218 activation of innate...     32          0    813
## [9]              GO:0002220 innate immune respon...      1          0    814

thits = gesel.search_set_text("9606", "cd? t cell")
print(gesel.fetch_some_sets("9606", thits[:10]))
##                        name             description   size collection number
##                      <list>                  <list> <list>     <list> <list>
## [0] HOFT_CD4_POSITIVE_AL... http://www.gsea-msig...     47         13     49
## [1] HOFT_CD4_POSITIVE_AL... http://www.gsea-msig...     28         13    131
## [2] HOFT_CD4_POSITIVE_AL... http://www.gsea-msig...     40         13    204
## [3] HOFT_CD4_POSITIVE_AL... http://www.gsea-msig...     16         13    252
## [4] HOFT_CD4_POSITIVE_AL... http://www.gsea-msig...     24         13    296
## [5] HOFT_CD4_POSITIVE_AL... http://www.gsea-msig...     42         13    316
## [6] HOFT_CD4_POSITIVE_AL... http://www.gsea-msig...     41         13    320
## [7] HOFT_CD4_POSITIVE_AL... http://www.gsea-msig...      6         13    323
## [8] QI_CD4_POSITIVE_ALPH... http://www.gsea-msig...      9         13    327
## [9] QI_NAIVE_T_CELL_ZOST... http://www.gsea-msig...      7         13    328
```

Users can construct powerful queries by intersecting the sets recovered from `search_set_text()` with those from `find_overlapping_sets()`.

```python
import biocutils
cancer_sets = biocutils.intersect(chits, overlaps["set"])
info = gesel.fetch_some_sets("9606", cancer_sets)
m = biocutils.match(cancer_sets, overlaps["set"])
info = info.set_column("count", [len(overlaps["genes"][r]) for r in m])

# We'll just use the proportion of enriched genes for ranking here;
# a more sophisticated analysis might compute a hypergeometric p-value.
prop = [info["count"][i] / info["size"][i] for i in range(info.shape[0])]
ordered = info[biocutils.order(prop, decreasing=True),:]
print(ordered)
## BiocFrame with 14 rows and 6 columns
##                         name             description   size collection number  count
##                       <list>                  <list> <list>     <list> <list> <list>
##  [0] LOPES_METHYLATED_IN_... http://www.gsea-msig...     28          2    903      1
##  [1] SCHLESINGER_H3K27ME3... http://www.gsea-msig...     28          2   2864      1
##  [2] WATANABE_COLON_CANCE... http://www.gsea-msig...     29          2     78      1
##                          ...                     ...    ...        ...    ...    ...
## [11] ACEVEDO_LIVER_CANCER_DN http://www.gsea-msig...    540          2   3150      1
## [12] SMID_BREAST_CANCER_L... http://www.gsea-msig...    587          2    991      1
## [13] LIU_OVARIAN_CANCER_T... http://www.gsea-msig...   1713          2   2003      1
```

## Fetching all data

**gesel** is designed around partial extraction from the database files, but it may be more efficient to pull all of the data into memory at once.
This is most useful for the gene set details, which can be retrieved _en masse_:

```python
set_info = gesel.fetch_all_sets("9606")
print(set_info)
## BiocFrame with 40654 rows and 5 columns
##                            name             description   size collection number
##                          <list>                  <list> <list>     <list> <list>
##     [0]              GO:0000002 mitochondrial genome...     11          0      0
##     [1]              GO:0000003            reproduction      4          0      1
##     [2]              GO:0000009 alpha-1,6-mannosyltr...      2          0      2
##                             ...                     ...    ...        ...    ...
## [40651] HALLMARK_KRAS_SIGNAL... http://www.gsea-msig...    200         15     47
## [40652] HALLMARK_KRAS_SIGNAL... http://www.gsea-msig...    200         15     48
## [40653] HALLMARK_PANCREAS_BE... http://www.gsea-msig...     40         15     49
```

The set indices returned by other functions like `find_overlapping_sets()` can then be used to directly subset the `set_info` data frame by row.
In fact, calling `fetch_some_sets()` after `fetch_all_sets()` will automatically use the data frame created by the latter,
instead of attempting another request to the database.
The same approach can be used to extract collection information, via `fetch_all_collections()`;
gene set membership, via `fetch_genes_for_all_sets()`;
and the sets containing each gene, via `fetch_sets_for_all_genes()`.

## Advanced use 

**gesel** uses a lot of in-memory caching to reduce the number of requests to the database files within a single Python session.
On rare occasions, the cache may become outdated, e.g., if the database files are updated while an Python session is running.
Users can prompt **gesel** to re-acquire all data by flusing the cache:

```python
gesel.flush_memory_cache()
```

Applications can specify their own functions for obtaining files (or byte ranges thereof) by passing a custom `config=` in each **gesel** function.
For example, on a shared HPC filesystem, we could point **gesel** towards a directory of Gesel database files.
This provides a performant alternative to HTTP requests for an institutional collection of gene sets.
