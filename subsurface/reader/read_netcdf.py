import warnings

import xarray as xr

from subsurface import UnstructuredData, StructuredData


__all__ = ['read_unstruct', 'read_struct']


def read_unstruct(path, legacy=False, **kwargs):
    ds = xr.open_dataset(path, **kwargs)

    if legacy is False:
        try:
            ud = UnstructuredData(ds)
        except KeyError:
            warnings.warn("Trying loading legacy files.")
            ud = read_unstruct(path, legacy=True)
    else:
        ud = _legacy_read_unstruct(ds)
    return ud


def _legacy_read_unstruct(ds):
    xarray_dict = {
        "vertex": ds.vertex,
        "cells": ds.cells,
        "cell_attrs": ds.attributes.rename({"attribute": "cell_attr"}),
        "vertex_attrs": ds.points_attributes.rename({"points_attribute": "vertex_attr"})
    }
    ud = UnstructuredData.from_data_arrays_dict(xarray_dict, ds.coords, ds.attrs)
    return ud


def read_struct(path, **kwargs):
    ds = xr.open_dataset(path, **kwargs)
    return StructuredData(ds)
