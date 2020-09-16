import pytest

from subsurface.structs import PointSet, TriSurf, LineSet, TetraMesh
from subsurface.structs.base_structures import UnstructuredData
import numpy as np
import pandas as pd


@pytest.fixture(scope='session')
def point_set():
    n = 100

    data = UnstructuredData(
        vertex=np.random.rand(n, 3),
        edges=np.random.rand(n, 0),
        attributes=pd.DataFrame({'foo': np.arange(n)})
    )

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

    data = UnstructuredData(
        vertex=vertices,
        edges=faces,
        attributes=pd.DataFrame({'foo': np.arange(faces.shape[0])})
    )

    trisurf = TriSurf(data)
    return trisurf


@pytest.fixture(scope='session')
def line_set():
    n = 100

    theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
    z = np.linspace(-2, 2, 100)
    r = z**2 + 1
    x = r * np.sin(theta)
    y = r * np.cos(theta)
    v = np.column_stack((x, y, z))

    data = UnstructuredData(
        vertex=v,
        edges=np.random.rand(n-1, 2),
        attributes=pd.DataFrame({'foo': np.arange(n-1)})
    )

    lineset = LineSet(data)
    lineset.generate_default_edges()
    return lineset


@pytest.fixture(scope='session')
def tetra_set():
    vertices = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [1, 1, 0],
                         [0, 1, 1]])
    edges = np.array([[0, 1, 2, 3], ])

    data = UnstructuredData(
        vertex=vertices,
        edges=edges,
        attributes=pd.DataFrame({'foo': np.arange(edges.shape[0])})
    )

    tets = TetraMesh(data)
    return tets