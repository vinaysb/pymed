""" Python wrapper for PubMed API """

from .pymed import PubMed
from .version import __version__

__all__ = ["PubMed", "__version__"]
