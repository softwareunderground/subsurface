import xarray as xr

from subsurface import UnstructuredData, StructuredData


def read_unstruct(path, **kwargs):
    ds = xr.open_dataset(path, **kwargs)
    return UnstructuredData(ds=ds)


def read_struct(path, **kwargs):
    ds = xr.open_dataset(path, **kwargs)
    return StructuredData(data=ds)