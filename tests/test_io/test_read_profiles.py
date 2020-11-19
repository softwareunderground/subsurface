import geopandas as gpd
from subsurface import UnstructuredData, TriSurf
from subsurface.io.profiles import create_mesh_cross_section
from subsurface.visualization import to_pyvista_mesh, pv_plot
import imageio
import numpy as np


def test_read_trace_to_unstruct(data_path):
    traces = gpd.read_file(data_path + '/profiles/Traces.shp')
    v, e = create_mesh_cross_section(
        traces.loc[0, 'geometry'],
        traces.loc[0, 'zmax'],
        traces.loc[0, 'zmin'],
    )
    print(traces)
    unstruct = UnstructuredData(v, e)
    ts = TriSurf(unstruct)
    s = to_pyvista_mesh(ts)
    origin = [traces.loc[0, 'geometry'].xy[0][0],
              traces.loc[0, 'geometry'].xy[1][0],
              traces.loc[0, 'zmin']]
    point_u = [traces.loc[0, 'geometry'].xy[0][-1],
               traces.loc[0, 'geometry'].xy[1][-1],
               traces.loc[0, 'zmin']]
    point_v = [traces.loc[0, 'geometry'].xy[0][0],
               traces.loc[0, 'geometry'].xy[1][0],
               traces.loc[0, 'zmax']]

    s.texture_map_to_plane(
        inplace=True,
        origin=origin,
        point_u=point_u,
        point_v=point_v
    )
    cross = imageio.imread(data_path + '/profiles/Profil1_cropped.png')
    import pyvista as pv
    tex = pv.numpy_to_texture(cross)
    pv_plot([s], image_2d=False, add_mesh_kwargs={
        'texture': tex
    }
            )


def test_read_trace_to_struct(data_path):
    raise NotImplementedError
    traces = gpd.read_file(data_path + '/profiles/Traces.shp')
    cross = imageio.imread(data_path + '/profiles/Profil1_cropped.png')
    import xarray as xr
    line_string = traces.loc[0, 'geometry']
    from scipy.interpolate import interp1d
    f = interp1d(traces.loc[0, 'geometry'].xy[0],
                 traces.loc[0, 'geometry'].xy[1])
    xnew = np.linspace(traces.loc[0, 'geometry'].xy[0][0],
                       traces.loc[0, 'geometry'].xy[0][-1],
                       num=cross.shape[0],
                       endpoint=True)

    xarr = xr.DataArray(
        data=cross,
        dims=['x', 'y', 'z', 'rgb'],
        coords={'xy': (['x', 'y'], np.ones((cross.shape[0], 2)))}
    )

    print(xarr)
