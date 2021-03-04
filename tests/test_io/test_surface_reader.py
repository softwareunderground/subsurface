import pytest
import pandas as pd
from pyvista import UnstructuredGrid

from subsurface.reader.mesh import surface_reader
from subsurface.structs import TetraMesh, TriSurf
from subsurface.structs.base_structures import UnstructuredData
import os
from subsurface.visualization.to_pyvista import pv_plot, to_pyvista_mesh

input_path = os.path.dirname(__file__) + '/../data'


@pytest.fixture(scope="module")
def get_unstructured_data() -> UnstructuredData:
    fp = input_path + "/land_surface_vertices.csv"
    ud = surface_reader.read_2d_mesh(fp)
    return ud


@pytest.fixture(scope="module")
def get_less_unstructured_data() -> UnstructuredData:
    fp = input_path + "/less_land_surface_vertices.csv"
    ud_less = surface_reader.read_2d_mesh(fp)
    return ud_less


@pytest.fixture(scope="module")
def get_unstructured_data_with_cells() -> UnstructuredData:
    fp = input_path + "/vertices_and_edges.csv"
    ud_cells = surface_reader.read_2d_mesh(
        fp,
        columns_map={
            'x': 'x',
            'y': 'y',
            'z': 'z',
            '0': 'e1',
            '1': 'e2',
            '2': 'e3'
        }
    )
    return ud_cells


@pytest.fixture(scope="module")
def get_unstructured_data_with_attribute() -> UnstructuredData:
    fp = input_path + "/well_based_temperature.csv"
    ud_attribute = surface_reader.read_2d_mesh(
        fp,
        columns_map={
            'x': 'x',
            'y': 'y',
            'z': 'z',
            '0': 'e1',
            '1': 'e2',
            '2': 'e3'
        },
        attribute_cols={'T': 3})
    return ud_attribute


def test_read_surface():
    # Read a csv which column names are already right
    fp = input_path + "/land_surface_vertices.csv"
    ud = surface_reader.read_2d_mesh(fp)
    print(ud)

    # Try reading a column with no index
    with pytest.raises(KeyError):
        fp = input_path + "/less_land_surface_vertices_no_col.csv"
        ud = surface_reader.read_2d_mesh(fp)
        print(ud)

    # Say pandas that there is no header and the name of the columns
    fp = input_path + "/less_land_surface_vertices_no_col.csv"
    ud = surface_reader.read_2d_mesh(fp, header=0, names=['x', 'y', 'z'])
    print(ud)

    # Remap column names to fit the requirements
    fp = input_path + "/less_land_surface_vertices_wrong_col.csv"
    ud = surface_reader.read_2d_mesh(
        fp,
        columns_map={'foo': 'x', 'bar': 'y', 'baz': 'z'})
    print(ud)
    return ud


def test_return_type_1(get_unstructured_data):
    assert isinstance(get_unstructured_data, UnstructuredData)


def test_return_type_2(get_unstructured_data_with_attribute):
    assert isinstance(get_unstructured_data_with_attribute, UnstructuredData)


def test_dataframes(get_unstructured_data):
    assert len(get_unstructured_data.vertex) == 132695
    assert len(get_unstructured_data.cells) == 263894


def test_cells_shape(get_unstructured_data):
    assert get_unstructured_data.cells.shape[1] == 3


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


def test_plot_cells_pyvista(get_unstructured_data_with_cells):
    ts = TriSurf(get_unstructured_data_with_cells)
    s = to_pyvista_mesh(ts)
    pv_plot([s], image_2d=True)


def test_plot_attributes_pyvista(get_unstructured_data_with_attribute):
    ts = TriSurf(get_unstructured_data_with_attribute)
    s = to_pyvista_mesh(ts)
    pv_plot([s], image_2d=True)
