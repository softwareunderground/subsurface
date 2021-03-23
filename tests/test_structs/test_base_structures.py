import pytest
from subsurface import TriSurf, StructuredGrid
from subsurface.reader.read_netcdf import read_unstruct, read_struct
from subsurface.reader.topography.topo_core import read_structured_topography

from subsurface.structs.base_structures import UnstructuredData, StructuredData
import numpy as np
import pandas as pd
import xarray as xr

from subsurface.structs.base_structures.common_data_utils import replace_outliers
from subsurface.visualization import to_pyvista_mesh, pv_plot, to_pyvista_grid


def test_unstructured_data():
    # Normal constructor
    foo = UnstructuredData.from_array(np.ones((5, 3)), np.ones((4, 3)),
                                      pd.DataFrame({'foo': np.arange(4)}))
    print(foo)

    # No attributes
    foo = UnstructuredData.from_array(np.ones((5, 3)), np.ones((4, 3)))
    print(foo)

    # Failed validation
    with pytest.raises(ValueError):
        foo = UnstructuredData.from_array(np.ones((5, 3)), np.ones((4, 3)),
                                          pd.DataFrame({'foo': np.arange(1)}))
        print(foo)


def test_unstructured_data_no_cells():
    foo = UnstructuredData.from_array(np.ones((5, 3)), cells="points")
    print(foo)


def test_unstructured_data_no_cells_no_attributes():
    attributes = {'notAttributeName': xr.DataArray(pd.DataFrame({'foo': np.arange(4)}))}

    with pytest.raises(KeyError):
        foo = UnstructuredData.from_array(vertex=np.ones((5, 3)), cells=np.ones((4, 3)),
                                          attributes=attributes)

    attributes2 = {
        'notAttributeName': xr.DataArray(
            pd.DataFrame({'foo': np.arange(4)}),
            dims=['cell', 'cell_attr']
        )}

    foo = UnstructuredData.from_array(vertex=np.ones((5, 3)), cells=np.ones((4, 3)),
                                                attributes=attributes2)

    print(foo)


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
    b = StructuredData.from_data_array(b0)
    print(b)

    # StructuredData from np.array
    c = StructuredData.from_numpy(xx)
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

    s3 = xr.Dataset({'foo': (['x', 'y', 'z'], xx)})
    print(s3)


def test_read_unstruct(data_path):
    us = read_unstruct(data_path + '/interpolator_meshes.nc')
    trisurf = TriSurf(us)
    s = to_pyvista_mesh(trisurf)
    pv_plot([s], image_2d=True)


def test_read_struct(data_path):
    s = read_struct(data_path + '/interpolator_regular_grid.nc')
    sg = StructuredGrid(s)
    s = to_pyvista_grid(sg,
                        data_set_name='block_matrix',
                        attribute_slice={'Properties': 'id',
                                         'Features': 'Default series'})

    pv_plot([s], image_2d=True)


def test_remove_outliers(data_path):
    topo_path = data_path + '/topo/dtm_rp.tif'
    struct = read_structured_topography(topo_path)
    replace_outliers(struct, 'topography', 0.99)
    print(struct.data['topography'])
    print(struct.data['topography'].min())
