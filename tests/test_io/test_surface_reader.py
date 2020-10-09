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


@pytest.fixture(scope="module")
def get_unstructured_data_with_edges() -> UnstructuredData:
    fp = input_path + "/vertices_and_edges.csv"
    ud_edges = surface_reader.read_in_surface_vertices(fp)
    return ud_edges


def test_return_type(get_unstructured_data):
    assert isinstance(get_unstructured_data, UnstructuredData)


def test_dataframes(get_unstructured_data):
    assert len(get_unstructured_data.vertex) == 132695
    assert len(get_unstructured_data.edges) == 263894


def test_edges_shape(get_unstructured_data):
    print(get_unstructured_data.vertex)
    assert get_unstructured_data.edges.shape[1] == 3


def test_unstructured_element(get_less_unstructured_data):
    ts = TriSurf(get_less_unstructured_data)
    assert len(ts.triangles) == 17
    assert isinstance(ts, TriSurf)


def test_plot_pyvista(get_unstructured_data):
    ts = TriSurf(get_unstructured_data)
    s = to_pyvista_mesh(ts)
    pv_plot([s], image_2d=True)


def test_plot_less_pyvista(get_less_unstructured_data):
    ts = TriSurf(get_less_unstructured_data)
    s = to_pyvista_mesh(ts)
    pv_plot([s], image_2d=True)


def test_plot_edges_pyvista(get_unstructured_data_with_edges):
    ts = TriSurf(get_unstructured_data_with_edges)
    s = to_pyvista_mesh(ts)
    pv_plot([s], image_2d=True)