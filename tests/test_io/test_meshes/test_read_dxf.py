import pytest

from conftest import RequirementsLevel
from subsurface.core.structs import UnstructuredData
from subsurface import TriSurf, PointSet, optional_requirements
from subsurface.modules.reader.mesh.surfaces_api import read_2d_mesh_to_unstruct
from subsurface.core.reader_helpers.readers_data import ReaderFilesHelper
from subsurface.core.reader_helpers.reader_unstruct import ReaderUnstructuredHelper
import subsurface.modules.visualization as sb_viz

import numpy as np
import pandas


@pytest.mark.skipif(
    condition=(RequirementsLevel.MESH | RequirementsLevel.PLOT) not in RequirementsLevel.REQUIREMENT_LEVEL_TO_TEST(),
    reason="Need to set the READ_WELL variable to run this test"
)
class TestReadDxfAndPlot:
    def test_read_dxf_only_vertex(self, data_path):
        path = data_path + '/surfaces/shafts_small.dxf'

        foo = ReaderUnstructuredHelper(ReaderFilesHelper(path))

        unstruct = read_2d_mesh_to_unstruct(foo, delaunay=False)

        p = PointSet(unstruct)
        s = sb_viz.to_pyvista_points(p)

        sb_viz.pv_plot([s], image_2d=True)  # ? The 2D plot is not working

    def test_read_dxf_into_mesh(self, data_path):
        path = data_path + '/surfaces/shafts_small.dxf'
        from subsurface.modules.reader.mesh.dxf_reader import dxf_file_to_unstruct_input

        vertex, cells, cell_attr_int, cell_attr_map = dxf_file_to_unstruct_input(path)

        min = vertex.min(axis=0)
        tri_array_shifted = vertex - min

        trimesh = optional_requirements.require_trimesh()
        tri = trimesh.Trimesh(tri_array_shifted, faces=cells, face_attributes={"Shaft id": cell_attr_int})
        print(tri.bounds)
        print(tri)

        unstruct = UnstructuredData.from_array(
            np.array(tri.vertices),
            np.array(tri.faces),
            cells_attr=pandas.DataFrame(np.array(tri.face_attributes["Shaft id"]),
                                        columns=["Shaft id"]),
            xarray_attributes={
                    "bounds"       : tri.bounds.tolist(),
                    "cell_attr_map": cell_attr_map
            },
        )

        ts = TriSurf(mesh=unstruct)
        s = sb_viz.to_pyvista_mesh(ts)
        sb_viz.pv_plot([s], image_2d=True)

    def test_read_dxf_into_mesh_split_by_bodies(self, data_path):
        path = data_path + '/surfaces/shafts_small.dxf'
        from subsurface.modules.reader.mesh.dxf_reader import dxf_file_to_unstruct_input
        import trimesh
        import numpy as np
        import pandas
        vertex, cells, cell_attr_int, cell_attr_map = dxf_file_to_unstruct_input(path)

        tri_full = trimesh.Trimesh(vertex, faces=cells, face_attributes={"Shaft id": cell_attr_int})
        prev_n_cells = 0

        for e, tri in enumerate(tri_full.split()):
            vertex = np.array(tri.vertices)
            cells = np.array(tri.faces)

            n_cells = cells.shape[0]
            attr_ = tri_full.face_attributes["Shaft id"][prev_n_cells:prev_n_cells + n_cells]
            prev_n_cells += n_cells

            cells_attr = pandas.DataFrame(np.array(attr_), columns=["Shaft id"])

            unstruct = UnstructuredData.from_array(
                vertex,
                cells,
                cells_attr=cells_attr,
                xarray_attributes={
                        "bounds"       : tri.bounds.tolist(),
                        "cell_attr_map": cell_attr_map
                },
            )

            ts = TriSurf(mesh=unstruct)
            s = sb_viz.to_pyvista_mesh(ts)
            sb_viz.pv_plot([s], image_2d=True)


@pytest.mark.skipif(
    condition=(RequirementsLevel.MESH) not in RequirementsLevel.REQUIREMENT_LEVEL_TO_TEST(),
    reason="Need to set the READ_WELL variable to run this test"
)
class TestReadDxfNoPlot:
    def test_read_dxf_into_dirty_mesh(self, data_path):
        path = data_path + '/surfaces/shafts_small.dxf'
        from subsurface.modules.reader.mesh.dxf_reader import dxf_file_to_unstruct_input
        vertex, cells, cell_attr, cell_attr_map = dxf_file_to_unstruct_input(path)
        print("Vertex shape: ", vertex.shape)



