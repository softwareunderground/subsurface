import xarray as xr
import numpy as np


def test_write_unstruc(unstruc):
    a = xr.DataArray(unstruc.vertex, dims=['points', 'XYZ'])
    b = xr.DataArray(unstruc.cells, dims=['cells', 'node'])
    e = xr.DataArray(unstruc.attributes)
    c = xr.Dataset({'v': a, 'e': b, 'a': e})
    print(c)

