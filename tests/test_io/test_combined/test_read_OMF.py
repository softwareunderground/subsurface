import pyvista
from dotenv import dotenv_values

import subsurface
from conftest import RequirementsLevel
from subsurface import TriSurf, optional_requirements
from subsurface.visualization import to_pyvista_mesh, pv_plot
from subsurface.writer import base_structs_to_binary_file

import pytest

pytestmark = pytest.mark.skipif(
    condition=(RequirementsLevel.READ_MESH) not in RequirementsLevel.REQUIREMENT_LEVEL_TO_TEST(),
    reason="Need to set READ_MESH"
)


@pytest.fixture(scope="module")
def load_omf():
    config = dotenv_values()
    path = config.get('PATH_TO_OMF')
    omfvista = optional_requirements.require_omf()
    omf = omfvista.load_project(path)
    return omf


def test_omf_to_unstruct_single_block(load_omf):
    omf = load_omf

    block_name = omf.get_block_name(4)
    polydata_obj: pyvista.PolyData = omf[block_name]
    unstruct_pyvista: pyvista.UnstructuredGrid = polydata_obj.cast_to_unstructured_grid()
    cells_pyvista = unstruct_pyvista.cells.reshape(-1, 4)[:, 1:]

    unstruct: subsurface.UnstructuredData = subsurface.UnstructuredData.from_array(
        vertex=unstruct_pyvista.points,
        cells=cells_pyvista,
    )

    base_structs_to_binary_file("leapfrog1", unstruct)

    ts = TriSurf(mesh=unstruct)
    s = to_pyvista_mesh(ts)
    pv_plot([s], image_2d=True)


def test_omf_to_unstruct_all_surfaces(load_omf):
    omf = load_omf
    list_of_polydata: list[pyvista.PolyData] = []
    for i in range(omf.n_blocks):
        block: pyvista.PolyData = omf[i]
        cell_type = block.get_cell(0).type

        if cell_type == pyvista.CellType.TRIANGLE:
            pyvista_unstructured_grid: pyvista.UnstructuredGrid = block.cast_to_unstructured_grid()

            # * Create the unstructured data
            unstructured_data = subsurface.UnstructuredData.from_array(
                vertex=pyvista_unstructured_grid.points,
                cells=pyvista_unstructured_grid.cells.reshape(-1, 4)[:, 1:],
            )

            # * Convert subsurface object to pyvista again for plotting
            ts: subsurface.TriSurf = TriSurf(mesh=unstructured_data)
            s: pyvista.PolyData = to_pyvista_mesh(ts)

            list_of_polydata.append(s)

    pv_plot(list_of_polydata, image_2d=True)


def test_omf_from_stream_to_unstruct_all_surfaces():
    config = dotenv_values()
    path = config.get('PATH_TO_OMF')
    with open(path, "rb") as stream:
        list_unstructs = subsurface.reader.omf_stream_to_unstructs(stream)

    list_of_polydata: list[pyvista.PolyData] = []
    for unstruct in list_unstructs:
        ts: subsurface.TriSurf = TriSurf(mesh=unstruct)
        s: pyvista.PolyData = to_pyvista_mesh(ts)
        list_of_polydata.append(s)

    pv_plot(list_of_polydata, image_2d=True)
