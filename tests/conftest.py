import pytest

from subsurface.structs import PointSet, TriSurf, LineSet, TetraMesh
from subsurface.structs.base_structures import UnstructuredData
import numpy as np
import pandas as pd
import os


@pytest.fixture(scope='session')
def data_path():
    return os.path.abspath(os.path.dirname(__file__) + '/data')


@pytest.fixture(scope='session')
def unstruc():
    foo = UnstructuredData.from_array(np.ones((5, 3)), np.ones((4, 3)), pd.DataFrame({'foo': np.arange(4)}))
    return foo


@pytest.fixture(scope='session')
def point_set():
    n = 100

    data = UnstructuredData.from_array(vertex=np.random.rand(n, 3), cells=np.random.rand(n, 0),
                                       cells_attributes=pd.DataFrame({'foo': np.arange(n)}))

    pointset = PointSet(data)
    return pointset


@pytest.fixture(scope='session')
def tri_surf():
    vertices = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [1, 1, 0],
                         [0, 1, 0],
                         [0.5, 0.5, -1]])

    faces = np.vstack([[0, 1, 2],
                       [0, 1, 4],
                       [1, 2, 4]])

    data = UnstructuredData.from_array(vertex=vertices, cells=faces,
                                       cells_attributes=pd.DataFrame({'foo': np.arange(faces.shape[0])}))
    trisurf = TriSurf(data)
    return trisurf


@pytest.fixture(scope='session')
def line_set():
    n = 100

    theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
    z = np.linspace(-2, 2, 100)
    r = z ** 2 + 1
    x = r * np.sin(theta)
    y = r * np.cos(theta)
    v = np.column_stack((x, y, z))

    data = UnstructuredData.from_array(vertex=v, cells=np.random.rand(n - 1, 2),
                                       cells_attributes=pd.DataFrame({'foo': np.arange(n - 1)}))
    lineset = LineSet(data)
    lineset.generate_default_cells()
    return lineset


@pytest.fixture(scope='session')
def tetra_set():
    vertices = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [1, 1, 0],
                         [0, 1, 1]])
    cells = np.array([[0, 1, 2, 3], ])

    data = UnstructuredData.from_array(vertex=vertices, cells=cells,
                                       cells_attributes=pd.DataFrame({'foo': np.arange(cells.shape[0])}))

    tets = TetraMesh(data)
    return tets


@pytest.fixture(scope='session')
def struc_data():
    xrng = np.arange(-10, 10, 5)
    yrng = np.arange(-10, 10, 7)
    zrng = np.arange(-10, 10, 2)
    grid_3d = np.meshgrid(xrng * 10, yrng * 100, zrng * 1000, indexing='ij')
    grid_2d = np.meshgrid(xrng * 20, yrng * 200, indexing='ij')
    return grid_3d, grid_2d, xrng, yrng, zrng
