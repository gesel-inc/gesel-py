from typing import Optional
from . import _utils as utils


def download_gene_file(
    name: str,
    url: Optional[str] = None,
    cache: Optional[str] = None,
    overwrite: bool = False
) -> str:
    """
    Download Gesel gene files and store them in a cache on the local file system.

    Args:
        name:
            Name of the file.
            This usually has the species identifier as a prefix.

        url:
            Base URL to the Gesel gene files.
            If ``None``, it is set to :py:func:`~gene_url`.

        cache:
            Path to a cache directory.
            If ``None``, it is set to :py:func:`~cache_directory`.

        overwrite:
            Boolean indicating whether any cached file should be overwritten with a new download.

    Returns:
        Path to the downloaded file on the local file system.

    Examples:
        >>> import gesel
        >>> gesel.download_gene_file("9606_symbol.tsv.gz")
    """
    if url is None:
        url = gene_url()
    return utils._download_file(cache, url + "/" + name, overwrite)


_gene_url = None


def gene_url(url: Optional[str] = None) -> str:
    """
    Get or set the base URL to the Gesel gene files, which is used in :py:func:`~download_gene_file`.

    Args:
        url: 
            The new gene URL.

    Returns:
        If ``url = None``, the URL to the Gesel gene is returned.
        The default gene URL is set to the `GitHub releases page <https://github.com/LTLA/gesel-feedstock>`_.
        This can be altered by setting the ``GESEL_GENE_URL`` environment variable.

        If ``url`` is provided, this function sets the gene URL to ``url``, and returns the previous value of the URL.

    Examples:
        >>> import gesel
        >>> gesel.gene_url()
        >>> old = gesel.gene_url("https://foo.bar")
        >>> gesel.gene_url(old)
        >>> gesel.gene_url()
    """

    global _gene_url
    if _gene_url is None:
        import os
        if "GESEL_GENE_URL" in os.environ:
            _gene_url = os.environ["GESEL_GENE_URL"]
        else:
            _gene_url = "https://github.com/LTLA/gesel-feedstock/releases/download/genes-v1.0.0"

    previous = _gene_url
    if url is not None:
        _gene_url = url
    return previous
