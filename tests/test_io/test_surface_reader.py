import pytest
import pandas as pd
from subsurface.io.grids import surface_reader
from subsurface.structs.base_structures import UnstructuredData
import os

input_path = os.path.dirname(__file__)+'/../data'


@pytest.fixture(scope="module")
def get_unstructured_data() -> UnstructuredData:
    fp = input_path + "/land_surface_vertices.csv"
    unstrdata = surface_reader.read_in_surface_vertices(fp)
    return unstrdata


def test_return_type(get_unstructured_data):
    assert isinstance(get_unstructured_data, UnstructuredData)


def test_dataframes(get_unstructured_data):
    assert len(get_unstructured_data.vertex) == 132695
    assert len(get_unstructured_data.edges) == 863814


def test_edges_shape(get_unstructured_data):
    assert get_unstructured_data.edges.shape[1] == 4
#def test_plot_pyvista(get_unstructured_data):
    # tm = TetraMesh(get_unstructured_data)
    # s = to_pyvista_tetra(tm)
    # pv_plot([s], image_2d=True)
    # topo_df = pd.read_csv(input_path + "/land_surface_vertices.csv")
    # topo = pv.PolyData(topo_df.values).delaunay_2d()
    # topo.plot(notebook=False, show_grid=True)
#
# def test_land_surface_vertices_coords(get_vertices):
#     assert get_vertices.iloc[5][2] == 1493.90209961
#     assert get_vertices.iloc[-1][-1] == 2430.35742188