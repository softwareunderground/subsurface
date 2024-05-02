import os

import pytest

from conftest import RequirementsLevel
from subsurface.modules.reader.readers_data import ReaderUnstructuredHelper, ReaderFilesHelper
from subsurface.core.structs import TriSurf
from subsurface.core.structs.base_structures import UnstructuredData
from subsurface.modules.visualization.to_pyvista import pv_plot, to_pyvista_mesh
from subsurface.modules.reader.mesh.surfaces_api import read_2d_mesh_to_unstruct

input_path = os.path.dirname(__file__) + '/../../data/surfaces'

pytestmark = pytest.mark.skipif(
    condition=(RequirementsLevel.READ_MESH) not in RequirementsLevel.REQUIREMENT_LEVEL_TO_TEST(),
    reason="Need to set the READ_MESH"
)

@pytest.fixture(scope="module")
def get_less_unstructured_data() -> UnstructuredData:
    fp = input_path + "/less_land_surface_vertices.csv"
    ud_less = read_2d_mesh_to_unstruct(ReaderUnstructuredHelper(ReaderFilesHelper(fp)))
    return ud_less


@pytest.fixture(scope="module")
def get_unstructured_data_with_cells() -> UnstructuredData:
    fp = input_path + "/vertices_and_edges.csv"
    ud_cells = read_2d_mesh_to_unstruct(
        ReaderUnstructuredHelper(
            reader_vertex_args=ReaderFilesHelper(fp, usecols=['x', 'y', 'z']),
            reader_cells_args=ReaderFilesHelper(
                fp, usecols=['0', '1', '2'],
                columns_map={
                    '0': 'e1',
                    '1': 'e2',
                    '2': 'e3'
                }
            )
        )
    )
    return ud_cells


@pytest.fixture(scope="module")
def get_unstructured_data_with_attribute() -> UnstructuredData:
    fp = input_path + "/well_based_temperature.csv"
    reader_unstruc = ReaderUnstructuredHelper(
        reader_vertex_args=ReaderFilesHelper(fp, usecols=['x', 'y', 'z']),
        reader_vertex_attr_args=ReaderFilesHelper(fp, usecols=['T'])
    )

    ud_attribute = read_2d_mesh_to_unstruct(reader_unstruc)
    return ud_attribute


def test_read_surface2():
    # Try reading a column with no index
    with pytest.raises(KeyError):
        fp = input_path + "/less_land_surface_vertices_no_col.csv"
        reader_unstruc = ReaderUnstructuredHelper(reader_vertex_args=ReaderFilesHelper(fp))

        ud = read_2d_mesh_to_unstruct(reader_unstruc)
        print(ud)

    # Say pandas that there is no header and the name of the columns
    fp = input_path + "/less_land_surface_vertices_no_col.csv"
    reader_unstruc = ReaderUnstructuredHelper(
        reader_vertex_args=ReaderFilesHelper(fp, header=0, col_names=['x', 'y', 'z'])
    )
    ud = read_2d_mesh_to_unstruct(reader_unstruc)
    print(ud)

    # Remap column names to fit the requirements
    fp = input_path + "/less_land_surface_vertices_wrong_col.csv"
    reader_unstruc = ReaderUnstructuredHelper(
        reader_vertex_args=ReaderFilesHelper(fp, columns_map={'foo': 'x', 'bar': 'y', 'baz': 'z'})
    )

    ud = read_2d_mesh_to_unstruct(reader_unstruc)
    print(ud)
    return ud


def test_return_type_2(get_unstructured_data_with_attribute):
    assert isinstance(get_unstructured_data_with_attribute, UnstructuredData)


def test_cells_shape(get_less_unstructured_data):
    assert get_less_unstructured_data.cells.shape[1] == 3


def test_unstructured_element(get_less_unstructured_data):
    ts = TriSurf(get_less_unstructured_data)
    assert len(ts.triangles) == 17
    assert isinstance(ts, TriSurf)


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


def test_read_from_multiple_files():
    reader_vertex_args = ReaderFilesHelper(input_path + '/kim_vertices.csv', col_names=['x', 'y', 'z'])
    reader_edges_args = ReaderFilesHelper(input_path + '/kim_cells.csv', col_names=['e1', 'e2', 'e3'])
    reader_cells_attrs_args = ReaderFilesHelper(input_path + '/kim_cell_attributes.csv', col_names=['lith'])
    reader_vertex_attrs_args = ReaderFilesHelper(input_path + '/kim_point_attributes.csv', col_names=['lith_vertex'])

    reader_unstruc = ReaderUnstructuredHelper(reader_vertex_args, reader_edges_args,
                                              reader_vertex_attrs_args, reader_cells_attrs_args)

    ud = read_2d_mesh_to_unstruct(reader_unstruc)
    ts = TriSurf(ud)
    s = to_pyvista_mesh(ts)
    pv_plot([s], image_2d=True)
