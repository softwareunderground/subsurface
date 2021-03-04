import os

import pytest
import numpy as np

from subsurface.writer.to_rex.data_struct import RexMaterial
from subsurface.writer.to_rex.to_rex import RexMesh, numpy_to_rex, \
    write_rex_file, read_rex_file
from subsurface.reader.read_netcdf import read_unstruct, read_struct


@pytest.fixture(scope='module')
def unstruct(data_path):
    us = read_unstruct(data_path + '/interpolator_meshes.nc')
    return us


@pytest.fixture(scope='module')
def struct(data_path):
    s = read_struct(data_path + '/interpolator_regular_grid.nc')
    return s


def test_w_mesh_data_type(unstruct, save=False):
    rex_mesh = RexMesh(
        name='GemPy_Mesh',
        vertex=unstruct.data['vertex'].values,
        edges=unstruct.data['cells'].values,
        material_id=1  # unstruct.data['attributes'].values
    )

    rex_bytes = numpy_to_rex([rex_mesh])
    if save:
        write_rex_file(rex_bytes, os.path.abspath(os.path.dirname(__file__)+ '/solutions/one_mesh'))

    right_solution = read_rex_file(os.path.abspath(os.path.dirname(__file__)+'/solutions/one_mesh.rex'))
    assert rex_bytes == right_solution


def test_w_mesh_data_type_two_sides(unstruct, save=True):
    rex_mesh = RexMesh(
        name='GemPy_Mesh',
        vertex=unstruct.data['vertex'].values,
        edges=unstruct.data['cells'].values,
        material_id=1  # unstruct.data['attributes'].values
    )

    # Coping triangles to create the backside normal of the layers
    tri = unstruct.data['cells'].values
    tri_ = np.copy(tri)
    # TURN normals - One side of the normals
    tri_[:, 2] = tri[:, 1]
    tri_[:, 1] = tri[:, 2]

    rex_mesh_backside = RexMesh(
        name='GemPy_Mesh_back',
        vertex=unstruct.data['vertex'].values,
        edges=tri_,
        material_id=1  # unstruct.data['attributes'].values
    )

    rex_bytes = numpy_to_rex(rex_meshes=[rex_mesh, rex_mesh_backside])

    if save:
        write_rex_file(rex_bytes, os.path.abspath(os.path.dirname(__file__)+'./solutions/one_mesh_backside'))

    right_solution = read_rex_file(os.path.abspath(os.path.dirname(__file__)+'./solutions/one_mesh_backside.rex'))
    assert rex_bytes == right_solution


def test_w_material_data_type(unstruct, save=True):
    rex_material = RexMaterial(1, 0, 0, 1, 0, 0, 1, 0, 0)
    rex_bytes = numpy_to_rex(rex_material=[rex_material])
    if save:
        write_rex_file(rex_bytes, os.path.abspath(os.path.dirname(__file__)+'/solutions/one_material'))

    right_solution = read_rex_file(os.path.abspath(os.path.dirname(__file__)+'/solutions/one_material.rex'))
    assert rex_bytes == right_solution
