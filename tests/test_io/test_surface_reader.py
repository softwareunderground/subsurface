import pytest
import pandas as pd
from pyvista import UnstructuredGrid

from subsurface.io.grids import surface_reader
from subsurface.structs import TetraMesh
from subsurface.structs.base_structures import UnstructuredData
import os

from subsurface.visualization.to_pyvista import to_pyvista_tetra, pv_plot

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


@pytest.fixture(scope="module")
def get_vertices_and_edges() -> UnstructuredData:
    fp = input_path + "/vertices_and_edges.csv"
    ud_vae = surface_reader.read_in_surface_vertices(fp)
    return ud_vae


def test_return_type_ex1(get_unstructured_data):
    assert isinstance(get_unstructured_data, UnstructuredData)


def test_return_type_ex2(get_vertices_and_edges):
    assert isinstance(get_vertices_and_edges, UnstructuredData)


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
    tm = TetraMesh(get_less_unstructured_data)
    s = to_pyvista_tetra(tm)  # Process finished here with exit code 139 (interrupted by signal 11: SIGSEGV)
    assert isinstance(s, UnstructuredGrid)
    pv_plot([s], image_2d=True)


def test_plot_ex2_pyvista(get_vertices_and_edges):
    tm = TetraMesh(get_vertices_and_edges)
    s = to_pyvista_tetra(tm)
    assert isinstance(s, UnstructuredGrid)
    pv_plot([s], image_2d=True)
