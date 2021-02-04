import xarray as xr

from .profiles import *
from .wells.welly_reader import *
from .topography.topo_core import read_structured_topography, \
    read_unstructured_topography
from .wells import read_wells_to_unstruct
from .wells.wells_interface import borehole_location_to_unstruct


def read_unstruct(path, **kwargs):
    ds = xr.open_dataset(path, **kwargs)
    return UnstructuredData(ds=ds)


def read_struct(path, **kwargs):
    ds = xr.open_dataset(path, **kwargs)
    return StructuredData(data=ds)