from typing import Union, List
import numpy as np
from scipy.spatial.qhull import Delaunay
from shapely.geometry import LineString
import geopandas as gpd
import subsurface
from subsurface.visualization import to_pyvista_mesh, to_pyvista_line


def create_mesh_from_trace(linestring: LineString,
                           zmax: Union[float, int],
                           zmin: Union[float, int],
                           ):
    n = len(list(linestring.coords))
    coords = np.array([[x[0] for x in list(linestring.coords)],
                       [y[1] for y in list(linestring.coords)]]).T
    # duplicating the line, once with z=lower and another with z=upper values
    vertices = np.zeros((2 * n, 3))
    vertices[:n, :2] = coords
    vertices[:n, 2] = zmin
    vertices[n:, :2] = coords
    vertices[n:, 2] = zmax
    # i+n --- i+n+1
    # |\      |
    # | \     |
    # |  \    |
    # |   \   |
    # i  --- i+1

    tri = Delaunay(vertices[:, [0, 2]])
    faces = tri.simplices
    return vertices, faces


def create_tri_surf_from_traces_texture(
        path_to_trace,
        path_to_texture: Union[List[str]],
        idx=None
):
    args_list = traces_texture_to_sub_structs(path_to_trace,
                                              path_to_texture,
                                              idx)

    tri_surf_list = base_structs_to_tri_surf(args_list)

    meshes = [to_pyvista_mesh(i) for i in tri_surf_list]

    return meshes


def base_structs_to_tri_surf(args_list) -> List:
    ts_list = []
    for i in args_list:
        ts = subsurface.TriSurf(
            mesh=i[0],
            texture=i[1],
            texture_origin=i[2],
            texture_point_u=i[3],
            texture_point_v=i[4]
        )
        ts_list.append(ts)
    return ts_list


def traces_texture_to_sub_structs(path_to_trace, path_to_texture, idx):
    traces = gpd.read_file(path_to_trace)
    traces = _select_traces_by_index(idx, traces)

    base_args = []
    for index, row in traces.iterrows():
        v, e = create_mesh_from_trace(row['geometry'],
                                      row['zmax'],
                                      row['zmin'])
        unstruct = subsurface.UnstructuredData(v, e)

        import imageio
        cross = imageio.imread(path_to_texture[index])
        struct = subsurface.StructuredData(np.array(cross))

        origin = [row['geometry'].xy[0][0],
                  row['geometry'].xy[1][0],
                  row['zmin']]
        point_u = [row['geometry'].xy[0][-1],
                   row['geometry'].xy[1][-1],
                   row['zmin']]
        point_v = [row['geometry'].xy[0][0],
                   row['geometry'].xy[1][0],
                   row['zmax']]

        base_args.append((unstruct, struct, origin, point_u, point_v))
    return base_args


def line_set_from_trace(path_to_trace, idx=None):
    traces = gpd.read_file(path_to_trace)
    traces = _select_traces_by_index(idx, traces)

    mesh_list = []
    for index, row in traces.iterrows():
        s = len(row['geometry'].coords.xy[0])
        vertex = np.array((*row['geometry'].coords.xy,
                           np.zeros(s))).T
        unstruct = subsurface.UnstructuredData(vertex, 'lines')
        ls = subsurface.LineSet(unstruct)
        mesh_list.append(to_pyvista_line(ls, radius=10))

    return mesh_list


def _select_traces_by_index(idx, traces):
    if idx is not None:
        traces = traces.loc[idx]
    return traces
