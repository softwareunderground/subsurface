import pyvista as pv
from dataclasses import dataclass

from typing import Union, List

import numpy as np
import pandas as pd

import subsurface
from subsurface import optional_requirements
from subsurface.core.structs.unstructured_elements import TriSurf
from ...visualization import to_pyvista_line, to_pyvista_mesh


@dataclass
class TexturedMesh:
    unstruct: subsurface.UnstructuredData
    struct: subsurface.StructuredData
    origin_vector3: np.array
    point_u_vector3: np.array
    point_v_vector3: np.array


def create_mesh_from_trace(linestring, zmax: Union[float, int], zmin: Union[float, int]):
    from scipy.spatial.qhull import Delaunay
    if isinstance(linestring, list):
        linestring_coords = linestring
    else:  # ! For now I leave it as this because I am not sure with object geopandas returns
        linestring_coords = linestring.coords  # * Geopandas branch
    n = len(list(linestring_coords))
    coords = np.array([[x[0] for x in list(linestring_coords)],
                       [y[1] for y in list(linestring_coords)]]).T
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
        uv=None
):
    tri_surf: list[subsurface.TriSurf] = _traces_texture_to_sub_structs(
        path_to_trace=path_to_trace,
        path_to_texture=path_to_texture,
        idx=idx,
        uv=uv
    )

    pyvista_mesh = [to_pyvista_mesh(i) for i in tri_surf]

    return tri_surf, pyvista_mesh


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


def _traces_texture_to_sub_structs(path_to_trace, path_to_texture, idx, uv=None) -> list[TriSurf]:
    gpd = optional_requirements.require_geopandas()
    imageio = optional_requirements.require_imageio()

    traces = gpd.read_file(path_to_trace)
    traces = _select_traces_by_index(idx, traces)

    textured_mesh: list[TriSurf] = []
    n = 0
    for index, row in traces.iterrows():
        v, e = create_mesh_from_trace(row['geometry'], row['zmax'], row['zmin'])
        unstruct_mesh = subsurface.UnstructuredData.from_array(
            vertex=v,
            cells=e,
            vertex_attr=pd.DataFrame(np.zeros((v.shape[0], 2)), columns=['u', 'v'])
        )
        structured_data_texture = subsurface.StructuredData.from_numpy(
            array=np.array(imageio.v3.imread(path_to_texture[index]))
        )

        tri_surf = TriSurf(
            mesh=unstruct_mesh,
            texture=structured_data_texture,
            texture_origin=np.array([row['geometry'].xy[0][0], row['geometry'].xy[1][0], row['zmin']]),
            texture_point_u=np.array([row['geometry'].xy[0][-1], row['geometry'].xy[1][-1], row['zmin']]),
            texture_point_v=np.array([row['geometry'].xy[0][0], row['geometry'].xy[1][0], row['zmax']])
        )

        # * Set uv
        if uv is not None:
            uv_item = pd.DataFrame(uv[n], columns=['u', 'v'])
        else:
            uv_item = _get_uv_from_pyvista(tri_surf)
        tri_surf.mesh.points_attributes = uv_item
        
        textured_mesh.append(tri_surf)
        n += 1
    
    return textured_mesh


def _get_uv_from_pyvista(tri_surf: TriSurf) -> pd.DataFrame:
    pyvista = optional_requirements.require_pyvista()
    _mesh = to_pyvista_mesh(tri_surf)
    if tri_surf.texture is None:
        raise ValueError('unstructured_element needs texture data to be mapped.')
    _mesh.texture_map_to_plane(
        inplace=True,
        origin=tri_surf.texture_origin,
        point_u=tri_surf.texture_point_u,
        point_v=tri_surf.texture_point_v
    )
    tex = pv.numpy_to_texture(tri_surf.texture.values)
    _mesh._textures = {0: tex}
    from vtkmodules.util.numpy_support import vtk_to_numpy
    uv = vtk_to_numpy(_mesh.GetPointData().GetTCoords())

    return pd.DataFrame(uv, columns=['u', 'v'])


def _select_traces_by_index(idx, traces):
    if idx is not None:
        traces = traces.loc[idx]
    return traces
