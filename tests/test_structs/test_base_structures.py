import pytest

from subsurface.structs.base_structures import UnstructuredData, StructuredData
import numpy as np
import pandas as pd
import xarray as xr

def test_unstructured_data():
    # Normal constructor
    foo = UnstructuredData(np.ones((5, 3)), np.ones((4, 3)),
                           pd.DataFrame({'foo': np.arange(4)}))
    print(foo)

    # No attributes
    foo = UnstructuredData(np.ones((5, 3)), np.ones((4, 3)))
    print(foo)

    #Failed validation
    with pytest.raises(AttributeError, match=r".*edges must.*"):
        foo = UnstructuredData(np.ones((5, 3)), np.ones((4, 3)),
                               pd.DataFrame({'foo': np.arange(1)}))
        print(foo)


@pytest.fixture(scope='module')
def struc_data():
    xrng = np.arange(-10, 10, 2)
    yrng = np.arange(-10, 10, 2)
    zrng = np.arange(-10, 10, 2)
    grid_3d = np.meshgrid(xrng*10, yrng*100, zrng*1000)
    grid_2d = np.meshgrid(xrng*20, yrng*200)
    return grid_3d, grid_2d, xrng, yrng, zrng


def test_structured_data(struc_data):
    xx, yy, zz = struc_data[0]
    geo_map, high = struc_data[1]
    x_coord, y_coord, z_coord = struc_data[2:]
    s = xr.Dataset({'lith': (["x", "y", 'z'], xx),
                    'porosity': (["x", "y", 'z'], yy),
                    'something_else': (["x", "y", 'z'], zz),
                    'geo_map': (['x', 'y'], geo_map)},
                   coords={'x': x_coord, 'y': y_coord, 'z': z_coord})
    # StructuredData from Dataset
    a = StructuredData(s)
    print(a)

    # StructuredData from DataArray
    b0 = xr.DataArray(xx, coords={'x': x_coord, 'y': y_coord, 'z': z_coord},
                    dims=['x', 'y', 'z'])
    b = StructuredData(b0)
    print(b)

    # StructuredData from np.array
    c = StructuredData(xx)
    print(c)


def test_xarray():
    """this test is only to figure out how xarray works exactly"""
    xrng = np.arange(-10, 10, 2)
    yrng = np.arange(-10, 10, 2)
    zrng = np.arange(-10, 10, 2)
    xx, yy, zz = np.meshgrid(xrng, yrng, zrng)

    x_test, y_test = np.meshgrid(xrng, yrng)
    s0 = xr.DataArray(xx)
    print(s0)

    s1 = xr.DataArray(coords={'x': xrng, 'y': yrng, 'z': zrng}, dims=['x', 'y', 'z'])
    print(s1)

    s2 = xr.DataArray(xx, coords={'x': xrng, 'y': yrng, 'z': zrng},
                      dims=['x', 'y', 'z'])
    print(s2)


    # Each data set can be align to different dimensions that is why we need to specify
    # The coordinate name
    s = xr.Dataset({'xx': (["x", "y", 'z'], xx),
                    'yy': (["x", "y", 'z'], xx),
                    'zz': (["x", "y", 'z'], xx),
                    'foo': (['x', 'y'], x_test)},
                   coords={'x': xrng, 'y': yrng, 'z': zrng, 'bar': np.arange(3)})

    print(s)
    # Slice by data array
    print(s['xx'])

    # Slice by coordinate
    print(s[['x', 'y']])

    print(s['x'])

    print(type(s), '\n')

    s3 =  xr.Dataset({'foo': (['x', 'y', 'z'], xx)})
    print(s3)