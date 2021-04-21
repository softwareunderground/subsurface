from typing import Union, List

import numpy as np
import pandas as pd

import subsurface
from subsurface.visualization import to_pyvista_mesh_and_texture, to_pyvista_line


__all__ = ['create_mesh_from_trace', 'create_tri_surf_from_traces_texture',
           'base_structs_to_tri_surf', 'traces_texture_to_sub_structs',
           'lineset_from_trace']


def create_mesh_from_trace(linestring,
                           zmax: Union[float, int],
                           zmin: Union[float, int],
                           ):
    """

    Args:
        linestring (shapely.geometry.LineString):
        zmax:
        zmin:

    Returns:

    """
    from scipy.spatial.qhull import Delaunay

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
        idx=None,
        return_mesh=False,
        return_uv=False,
        uv=None
):
    args_list = traces_texture_to_sub_structs(path_to_trace, path_to_texture, idx, uv=uv)
    tri_surf_list = base_structs_to_tri_surf(args_list)
    meshes = None

    if return_mesh is True or return_uv is True:
        meshes_uv = [to_pyvista_mesh_and_texture(i) for i in tri_surf_list]
        meshes, uv = list(zip(*meshes_uv))
        if return_uv is True:
            tri_surf_list, meshes = create_tri_surf_from_traces_texture(path_to_trace, path_to_texture, idx=idx,
                                                                        return_mesh=return_mesh, return_uv=False, uv=uv)
    return tri_surf_list, meshes


def base_structs_to_tri_surf(args_list) -> List:
    ts_list = []
    for i in args_list:
        ts = subsurface.TriSurf(mesh=i[0], texture=i[1], texture_origin=i[2], texture_point_u=i[3],
                                texture_point_v=i[4])
        ts_list.append(ts)
    return ts_list


def traces_texture_to_sub_structs(path_to_trace, path_to_texture, idx, uv=None):
    import geopandas as gpd

    traces = gpd.read_file(path_to_trace)
    traces = _select_traces_by_index(idx, traces)

    base_args = []
    n = 0
    for index, row in traces.iterrows():
        v, e = create_mesh_from_trace(row['geometry'], row['zmax'], row['zmin'])
        if uv is not None:
            uv_item = pd.DataFrame(uv[n], columns=['u', 'v'])
        else:
            uv_item = None

        unstruct = subsurface.UnstructuredData.from_array(v, e, vertex_attr=uv_item)

        import imageio
        cross = imageio.imread(path_to_texture[index])
        struct = subsurface.StructuredData.from_numpy(np.array(cross))

        origin = [row['geometry'].xy[0][0], row['geometry'].xy[1][0], row['zmin']]
        point_u = [row['geometry'].xy[0][-1], row['geometry'].xy[1][-1], row['zmin']]
        point_v = [row['geometry'].xy[0][0], row['geometry'].xy[1][0], row['zmax']]

        base_args.append((unstruct, struct, origin, point_u, point_v))
        n += 1
    return base_args


def lineset_from_trace(path_to_trace, idx=None):
    import geopandas as gpd

    traces = gpd.read_file(path_to_trace)
    traces = _select_traces_by_index(idx, traces)

    mesh_list = []
    for index, row in traces.iterrows():
        s = len(row['geometry'].coords.xy[0])
        vertex = np.array((*row['geometry'].coords.xy,
                           np.zeros(s))).T
        unstruct = subsurface.UnstructuredData.from_array(vertex, 'lines')
        ls = subsurface.LineSet(unstruct)
        mesh_list.append(to_pyvista_line(ls, radius=10))

    return mesh_list


def _select_traces_by_index(idx, traces):
    if idx is not None:
        traces = traces.loc[idx]
    return traces
