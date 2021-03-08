import geopandas as gpd
import pytest

from subsurface import UnstructuredData, TriSurf, StructuredData
from subsurface.reader.profiles.profiles_core import create_mesh_from_trace, \
    create_tri_surf_from_traces_texture, lineset_from_trace
from subsurface.visualization import to_pyvista_mesh, pv_plot
import imageio
import numpy as np


def test_read_trace_to_unstruct(data_path):
    traces = gpd.read_file(data_path + '/profiles/Traces.shp')
    v, e = create_mesh_from_trace(traces.loc[0, 'geometry'], traces.loc[0, 'zmax'],
                                  traces.loc[0, 'zmin'])

    unstruct = UnstructuredData.from_array(v, e)

    cross = imageio.imread(data_path + '/profiles/Profil1_cropped.png')
    struct = StructuredData.from_numpy(np.array(cross))

    origin = [traces.loc[0, 'geometry'].xy[0][0],
              traces.loc[0, 'geometry'].xy[1][0],
              traces.loc[0, 'zmin']]
    point_u = [traces.loc[0, 'geometry'].xy[0][-1],
               traces.loc[0, 'geometry'].xy[1][-1],
               traces.loc[0, 'zmin']]
    point_v = [traces.loc[0, 'geometry'].xy[0][0],
               traces.loc[0, 'geometry'].xy[1][0],
               traces.loc[0, 'zmax']]

    ts = TriSurf(
        mesh=unstruct,
        texture=struct,
        texture_origin=origin,
        texture_point_u=point_u,
        texture_point_v=point_v
    )

    s = to_pyvista_mesh(ts)

    pv_plot([s], image_2d=True)


def test_tri_surf_from_traces_and_png(data_path):
    us, mesh_list = create_tri_surf_from_traces_texture(
        data_path + '/profiles/Traces.shp',
        path_to_texture=[
            data_path + '/profiles/Profil1_cropped.png',
            data_path + '/profiles/Profil2_cropped.png',
            data_path + '/profiles/Profil3_cropped.png',
            data_path + '/profiles/Profil4_cropped.png',
            data_path + '/profiles/Profil5_cropped.png',
            data_path + '/profiles/Profil6_cropped.png',
            data_path + '/profiles/Profil7_cropped.png',
        ],
        return_mesh=True,
        return_uv=False
    )

    pv_plot(mesh_list, image_2d=True)


def test_tri_surf_from_traces_and_png_uv(data_path):
    tri_surf, mesh_list = create_tri_surf_from_traces_texture(
        data_path + '/profiles/Traces.shp',
        path_to_texture=[
            data_path + '/profiles/Profil1_cropped.png',
            data_path + '/profiles/Profil2_cropped.png',
            data_path + '/profiles/Profil3_cropped.png',
            data_path + '/profiles/Profil4_cropped.png',
            data_path + '/profiles/Profil5_cropped.png',
            data_path + '/profiles/Profil6_cropped.png',
            data_path + '/profiles/Profil7_cropped.png',
        ],
        return_mesh=True,
        return_uv=True
    )

    print(tri_surf[0].mesh.points_attributes)
    pv_plot(mesh_list, image_2d=True)


def test_line_set_from_trace(data_path):
    m = lineset_from_trace(data_path + '/profiles/Traces.shp')
    pv_plot(m, image_2d=True)