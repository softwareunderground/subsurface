import pytest
from dotenv import dotenv_values

import subsurface
from conftest import RequirementsLevel
from subsurface import LineSet, UnstructuredData, PointSet, optional_requirements
from subsurface.visualization import pv_plot, to_pyvista_line, to_pyvista_points
from subsurface.writer import base_structs_to_binary_file

pytestmark = pytest.mark.skipif(
    condition=(RequirementsLevel.READ_MESH) not in RequirementsLevel.REQUIREMENT_LEVEL_TO_TEST(),
    reason="Need to set READ_MESH"
)

pyvista = optional_requirements.require_pyvista()


@pytest.fixture(scope="module")
def load_omf():
    config = dotenv_values()
    path = config.get('PATH_TO_BOLIDEN')
    omfvista = optional_requirements.require_omf()
    omf = omfvista.load_project(path)

    if plot := False:
        omf.plot(multi_colors=True, show_edges=True, notebook=False)
    return omf


def test_read_omf_with_pyvista(load_omf):
    omf = load_omf
    # ? For now I leave this commented out since we do not want to open a viewer


def test_omf_to_cylinders_to_collars(load_omf):
    pass


def test_omf_to_cylinders(load_omf):
    omf = load_omf
    block_name = omf.get_block_name(0)
    pyvista = optional_requirements.require_pyvista()
    polydata_obj: pyvista.PolyData = omf[block_name]
    # Grab only 20% of the data

    line = _polydata_to_unstruct(polydata_obj)
    index_of_collars = line.get_first_index_per_well("holeid")
    collars_unstruct = UnstructuredData.from_array(
        vertex= line.data.vertex[index_of_collars],
        cells="points",
        # cells_attr=collars_attributes.astype('float32'),
        # xarray_attributes={"wells_names": wells_names.values.tolist()})  # TODO: This should be int16!
    )

    p = to_pyvista_points(point_set=PointSet(data=collars_unstruct))
    s = to_pyvista_line(line, radius=10, as_tube=True, spline=False)
    s.set_active_scalars("holeid")

    if TO_LIQUID_EARTH := False:
        base_structs_to_binary_file("well", line.data)

    pv_plot([p, s], image_2d=True, add_mesh_kwargs={'point_size': 10})


def _polydata_to_unstruct(polydata_obj: 'pyvista.PolyData') -> LineSet:
    pd = optional_requirements.require_pandas()
    unstruct_pyvista: pyvista.UnstructuredGrid = polydata_obj.cast_to_unstructured_grid()
    cells_pyvista = unstruct_pyvista.cells.reshape(-1, 4)[:, 1:]
    grid = unstruct_pyvista
    cell_data = {name: grid.cell_data[name] for name in grid.cell_data}
    match polydata_obj.get_cell(0).type:
        case pyvista.CellType.LINE:
            cylinder_unstruct: subsurface.Unstructu
            cells_pyvista = unstruct_pyvista.cells.reshape(-1, 3)[:, 1:]
            cylinder_unstruct: subsurface.UnstructuredData = subsurface.UnstructuredData.from_array(
                vertex=unstruct_pyvista.points,
                cells=cells_pyvista,
                cells_attr=pd.DataFrame(cell_data)
            )

    line = LineSet(data=cylinder_unstruct)
    return  line
