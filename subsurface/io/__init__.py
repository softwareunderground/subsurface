import xarray as xr

from .wells.welly_reader import *
from .topography import read_structured_topography, read_unstructured_topography
from .wells import borehole_location_to_unstruct, read_wells_to_unstruct


def read_unstruct(path, **kwargs):
    ds = xr.open_dataset(path, **kwargs)
    return UnstructuredData(ds=ds)


def read_struct(path, **kwargs):
    ds = xr.open_dataset(path, **kwargs)
    return StructuredData(data=ds)