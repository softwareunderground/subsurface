import imageio
import pytest
from subsurface.reader.read_netcdf import read_unstruct
import json
import geopandas as gpd
import pytest
import numpy as np

from subsurface import UnstructuredData, TriSurf, StructuredData
from subsurface.reader.profiles.profiles_core import create_mesh_from_trace
from subsurface.visualization import to_pyvista_mesh, pv_plot, \
    to_pyvista_mesh_and_texture


@pytest.fixture(scope='module')
def unstruct(data_path):
    us = read_unstruct(data_path + '/interpolator_meshes.nc')
    return us


@pytest.fixture(scope='module')
def wells(data_path):
    us = read_unstruct(data_path + '/wells.nc')
    return us


def test_wells_to_binary(wells):
    bytearray_le, header = wells.to_binary()
    print(header)

    with open('well_f.json', 'w') as outfile:
        json.dump(header, outfile)

    new_file = open("wells_f.le", "wb")
    new_file.write(bytearray_le)


def test_profile_to_binary(data_path):
    traces = gpd.read_file(data_path + '/profiles/Traces.shp')
    v, e = create_mesh_from_trace(traces.loc[0, 'geometry'], traces.loc[0, 'zmax'],
                                  traces.loc[0, 'zmin'])

    unstruct_temp = UnstructuredData.from_array(v, e)

    cross = imageio.imread(data_path + '/profiles/Profil1_cropped.png')
    struct = StructuredData.from_numpy(np.array(cross))
    texture_binary, texture_header = struct.to_binary()

    origin = [traces.loc[0, 'geometry'].xy[0][0],
              traces.loc[0, 'geometry'].xy[1][0],
              int(traces.loc[0, 'zmin'])]
    point_u = [traces.loc[0, 'geometry'].xy[0][-1],
               traces.loc[0, 'geometry'].xy[1][-1],
               int(traces.loc[0, 'zmin'])]
    point_v = [traces.loc[0, 'geometry'].xy[0][0],
               traces.loc[0, 'geometry'].xy[1][0],
               int(traces.loc[0, 'zmax'])]

    texture_header['texture_origin'] = origin
    texture_header['texture_point_u'] = point_u
    texture_header['texture_point_v'] = point_v

    ts = TriSurf(
        mesh=unstruct_temp,
        texture=struct,
        texture_origin=origin,
        texture_point_u=point_u,
        texture_point_v=point_v
    )

    _, uv = to_pyvista_mesh_and_texture(ts)
    import pandas as pd

    unstruct = UnstructuredData.from_array(v, e, vertex_attr=pd.DataFrame(uv, columns=['u', 'v']))
    mesh_binary, mesh_header = unstruct.to_binary()

    with open('mesh_uv.json', 'w') as outfile:
        import json
        json.dump(mesh_header, outfile)

    with open('texture.json', 'w') as outfile:
        json.dump(texture_header, outfile)

    new_file = open("mesh_uv_f.le", "wb")
    new_file.write(mesh_binary)

    new_file = open("texture_f.le", "wb")
    new_file.write(texture_binary)

    return mesh_binary
