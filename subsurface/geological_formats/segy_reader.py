from typing import Union
from scipy.spatial.qhull import Delaunay
from shapely.geometry import LineString
from subsurface.structs.base_structures import StructuredData
import numpy as np

try:
    import segyio
    segyio_imported = True
except ImportError:
    segyio_imported = False


def read_in_segy(filepath: str, coords=None) -> StructuredData:
    """Reader for seismic data stored in sgy/segy files

    Args:
        filepath (str): the path of the sgy/segy file
        coords (dict): If data is a numpy array coords provides the values for
         the xarray dimension. These dimensions are 'x', 'y' and 'z'

    Returns: a StructuredData object with data, the traces with samples written into an xr.Dataset, optionally with
     labels defined by coords

    """

    segyfile = segyio.open(filepath, ignore_geometry=True)

    data = np.asarray([np.copy(tr) for tr in segyfile.trace[:]])

    sd = StructuredData.from_numpy(data)  # data holds traces * (samples per trace) values
    segyfile.close()
    return sd


def create_mesh_from_coords(coords: Union[dict, LineString],
                           zmin: Union[float, int], zmax: Union[float, int] = 0.0):
    """Creates a mesh for plotting StructuredData

    Args:
        coords (Union[dict, LineString]): the x and y, i.e. latitude and longitude, location of the traces of the seismic profile
        zmax (float): the maximum elevation of the seismic profile, by default 0.0
        zmin (float): the location in z where the lowest sample was taken

    Returns: vertices and faces for creating an UnstructuredData object

    """
    if type(coords) == LineString:
        linestring = coords
        n = len(list(linestring.coords))
        coords = np.array([[x[0] for x in list(linestring.coords)],
                           [y[1] for y in list(linestring.coords)]]).T
    else:
        n = len(coords['x'])
        coords = np.array([coords['x'],
                           coords['y']]).T
    # duplicating the line, once with z=lower and another with z=upper values
    vertices = np.zeros((2*n, 3))
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

