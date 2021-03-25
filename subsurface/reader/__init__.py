import warnings

from .profiles import *

from .topography.topo_core import read_structured_topography, read_unstructured_topography

from .readers_data import ReaderFilesHelper, ReaderWellsHelper, RawDataOptions

try:
    from . import wells
except ModuleNotFoundError:
    warnings.warn("Welly or Striplog not installed. No well reader possible.")

