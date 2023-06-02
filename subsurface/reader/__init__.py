import warnings

from .profiles import *

from .topography.topo_core import read_structured_topography, read_unstructured_topography

from .readers_data import ReaderFilesHelper, ReaderWellsHelper, RawDataOptions
from .mesh.omf_mesh_reader import omf_stream_to_unstructs
from .mesh.dxf_reader import dxf_stream_to_unstruct_input, dxf_file_to_unstruct_input

try:
    from . import wells
except ModuleNotFoundError:
    warnings.warn("Welly or Striplog not installed. No well reader possible.")

