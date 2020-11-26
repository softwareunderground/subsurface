import geopandas as gpd
import pytest

from subsurface import UnstructuredData, TriSurf, StructuredData
from subsurface.io.profiles import create_mesh_from_trace
from subsurface.visualization import to_pyvista_mesh, pv_plot
import imageio
import numpy as np


def test_read_trace_to_unstruct(data_path):
    traces = gpd.read_file(data_path + '/profiles/Traces.shp')
    v, e = create_mesh_from_trace(traces.loc[0, 'geometry'], traces.loc[0, 'zmax'],
                                  traces.loc[0, 'zmin'])

    unstruct = UnstructuredData(v, e)

    cross = imageio.imread(data_path + '/profiles/Profil1_cropped.png')
    struct = StructuredData(np.array(cross))

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

    pv_plot([s], image_2d=False)



