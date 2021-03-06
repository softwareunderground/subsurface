import pytest
import pandas as pd
import numpy as np

import subsurface as ss
from subsurface.structs import PointSet
from subsurface.structs.base_structures import UnstructuredData


def test_point_set_init(point_set):
    n = 100
    # Test check of number of cells:
    data = UnstructuredData.from_array(vertex=np.random.rand(n, 3), cells=np.random.rand(n, 3),
                                       cells_attr=pd.DataFrame({'foo': np.arange(n)}))

    with pytest.raises(AttributeError, match=r'.*must be.*'):
        pointset_break = PointSet(data)

    # Test Fixture
    print(point_set)
    assert point_set.point_data_dict['foo'][50] == 50


def test_tri_surf_init(tri_surf):
    # Test Fixture
    mesh = tri_surf
    assert mesh.mesh.n_points == 5
    assert mesh.n_triangles == 3


def test_line_set_init(line_set):
    # Default isinstantiation with automatic segment generation
    mesh = line_set
    assert mesh.n_segments == len(line_set.data.vertex) - 1


def test_tetra_mesh_init(tetra_set):
    mesh = tetra_set
    assert mesh.n_tetrahedrals == len(mesh.data.cells)


@pytest.mark.skip()
def test_curvi_mesh_init():
    xrng = np.arange(-10, 10, 2)
    yrng = np.arange(-10, 10, 2)
    zrng = np.arange(-10, 10, 2)
    xx, yy, zz = np.meshgrid(xrng, yrng, zrng)
    vertices = np.c_[xx.ravel(), yy.ravel(), zz.ravel()]

