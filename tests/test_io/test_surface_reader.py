import pytest
import pandas as pd
from pyvista import UnstructuredGrid

from subsurface.io.grids import surface_reader
from subsurface.structs import TetraMesh, TriSurf
from subsurface.structs.base_structures import UnstructuredData
import os

from subsurface.visualization.to_pyvista import to_pyvista_tetra, pv_plot, to_pyvista_mesh

input_path = os.path.dirname(__file__)+'/../data'


@pytest.fixture(scope="module")
def get_unstructured_data() -> UnstructuredData:
    fp = input_path + "/land_surface_vertices.csv"
    ud = surface_reader.read_in_surface_vertices(fp)
    return ud


@pytest.fixture(scope="module")
def get_less_unstructured_data() -> UnstructuredData:
    fp = input_path + "/less_land_surface_vertices.csv"
    ud_less = surface_reader.read_in_surface_vertices(fp)
    return ud_less


def test_return_type(get_unstructured_data):
    assert isinstance(get_unstructured_data, UnstructuredData)


def test_dataframes(get_unstructured_data):
    assert len(get_unstructured_data.vertex) == 132695
    assert len(get_unstructured_data.edges) == 863814


def test_edges_shape(get_unstructured_data):
    assert get_unstructured_data.edges.shape[1] == 4


def test_unstructured_element(get_less_unstructured_data):
    tm = TetraMesh(get_less_unstructured_data)
    assert len(tm.tetrahedrals) == 39
    assert isinstance(tm, TetraMesh)


def test_plot_pyvista(get_less_unstructured_data):
    ts = TriSurf(get_less_unstructured_data) # The element type should be TriSurf
    s = to_pyvista_mesh(ts) # Process finished here with exit code 139 (interrupted by signal 11: SIGSEGV)
    # assert isinstance(s, UnstructuredGrid) This assert is wrong
    pv_plot([s], image_2d=True)
#
# def test_land_surface_vertices_coords(get_vertices):
#     assert get_vertices.iloc[5][2] == 1493.90209961
#     assert get_vertices.iloc[-1][-1] == 2430.35742188