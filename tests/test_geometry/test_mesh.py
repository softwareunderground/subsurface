import pytest
import pandas as pd
import numpy as np

import subsurface as ss


def test_point_set_init():
    n = 100
    df = pd.DataFrame(np.random.rand(n, 3), columns=['x', 'y', 'z'])
    # Make the data structure
    pointset = ss.geometry.PointSet(df)
    assert pointset.n_points == n
    assert np.allclose(pointset.points, df[['x', 'y', 'z']])
    df['scalars'] = np.arange(n)
    pointset = ss.geometry.PointSet(df)
    assert pointset.n_points == n
    assert np.allclose(pointset.points, df[['x', 'y', 'z']])
    data = pointset.point_data
    assert np.allclose(data['scalars'], df['scalars'])


def test_tri_surf_init():
    vertices = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [1, 1, 0],
                         [0, 1, 0],
                         [0.5, 0.5, -1]])
    dfv = pd.DataFrame(vertices, columns=['x', 'y', 'z'])

    # mesh faces
    faces = np.vstack([[0, 1, 2],
                       [0, 1, 4],
                       [1, 2, 4]])
    dfc = pd.DataFrame(faces, columns=['a', 'b', 'c'])

    mesh = ss.geometry.TriSurf(dfv, dfc)
    assert mesh.n_points == 5
    assert mesh.n_triangles == 3

    # Now with cell and point data
    dfv['foo'] = np.random.rand(len(vertices))
    cd = pd.DataFrame(np.random.rand(len(faces), 2), columns=['a', 'b',])

    mesh = ss.geometry.TriSurf(dfv, dfc, cd)
    assert mesh.n_points == 5
    assert mesh.n_triangles == 3

    assert np.allclose(mesh.point_data['foo'], dfv['foo'])
    assert np.allclose(mesh.cell_data, cd)


def test_line_set_init():

    def make_points():
        """Helper to make XYZ points"""
        theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
        z = np.linspace(-2, 2, 100)
        r = z**2 + 1
        x = r * np.sin(theta)
        y = r * np.cos(theta)
        return np.column_stack((x, y, z))

    vertices = make_points()
    dfv = pd.DataFrame(vertices, columns=['x', 'y', 'z'])

    # Default isinstantiation with automatic segment generation
    mesh = ss.geometry.LineSet(dfv)
    assert mesh.n_points == len(vertices)
    assert mesh.n_segments == len(vertices) - 1


def test_tetra_mesh_init():
    # Single celled example
    vertices = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [1, 1, 0],
                         [0, 1, 1]])
    tets = np.array([[0, 1, 2, 3],])
    dfv = pd.DataFrame(vertices, columns=['x', 'y', 'z'])
    dft = pd.DataFrame(tets, columns=['a', 'b', 'c', 'd'])

    mesh = ss.geometry.TetraMesh(dfv, dft)
    assert mesh.n_points == len(vertices)
    assert mesh.n_tetrahedrals == len(tets)
