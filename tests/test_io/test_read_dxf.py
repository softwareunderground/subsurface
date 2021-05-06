from subsurface.structs import UnstructuredData

from subsurface import TriSurf, PointSet
from subsurface.reader import read_unstructured_topography
import subsurface.visualization as sb_viz
from subsurface.reader.mesh.surfaces_api import read_2d_mesh_to_unstruct
from subsurface.reader.readers_data import ReaderUnstructuredHelper, ReaderFilesHelper


def test_read_dxf_only_vertex(data_path):
    path = data_path + '/surfaces/shafts_small.dxf'

    foo = ReaderUnstructuredHelper(ReaderFilesHelper(path))

    unstruct = read_2d_mesh_to_unstruct(foo, delaunay=False)
    # ts = TriSurf(mesh=unstruct)
    # s = sb_viz.to_pyvista_mesh(ts)

    p = PointSet(unstruct)
    s = sb_viz.to_pyvista_points(p)

    sb_viz.pv_plot([s], image_2d=True)


def test_read_dxf_into_dirty_mesh(data_path):
    path = data_path + '/surfaces/shafts_small.dxf'
    from subsurface.reader.mesh.surface_reader import dxf_to_mesh
    vertex, cells, cell_attr, cell_attr_map = dxf_to_mesh(path)


def test_read_dxf_into_mesh(data_path):
    path = data_path + '/surfaces/shafts_small.dxf'
    from subsurface.reader.mesh.surface_reader import dxf_to_mesh
    import trimesh
    import numpy as np
    import pandas
    vertex, cells, cell_attr_int, cell_attr_map = dxf_to_mesh(path)

    tri = trimesh.Trimesh(vertex, faces=cells)
    print(tri.bounds)
    print(tri)

    unstruct = UnstructuredData.from_array(
        np.array(tri.vertices),
        np.array(tri.faces),
        cells_attr=pandas.DataFrame(cell_attr_int, columns=["Shaft id"]),
        xarray_attributes={"bounds": tri.bounds.tolist(),
                           "cell_attr_map": cell_attr_map
                           },
    )
    #from subsurface.writer import base_structs_to_binary_file
    #base_structs_to_binary_file("shafts", unstruct)

    ts = TriSurf(mesh=unstruct)
    s = sb_viz.to_pyvista_mesh(ts)
    sb_viz.pv_plot([s], image_2d=True)
