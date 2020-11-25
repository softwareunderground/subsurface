import xarray as xr

from .wells.welly_reader import *
from .topography import *
from .wells import *
from .. import UnstructuredData, StructuredData


def read_unstruct(path, **kwargs):
    ds = xr.open_dataset(path, **kwargs)
    return UnstructuredData(ds=ds)


def read_struct(path, **kwargs):
    ds = xr.open_dataset(path, **kwargs)
    return StructuredData(data=ds)