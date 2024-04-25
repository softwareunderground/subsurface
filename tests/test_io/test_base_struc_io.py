import xarray as xr
import numpy as np


def test_write_unstruc(unstruct_factory):
    a = xr.DataArray(unstruct_factory.vertex, dims=['points', 'XYZ'])
    b = xr.DataArray(unstruct_factory.cells, dims=['cells', 'node'])
    e = xr.DataArray(unstruct_factory.attributes)
    c = xr.Dataset({'v': a, 'e': b, 'a': e})
    print(c)

