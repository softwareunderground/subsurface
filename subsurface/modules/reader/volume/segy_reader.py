from typing import Union

from subsurface import optional_requirements
from ....core.structs.base_structures import StructuredData
import numpy as np


def read_in_segy(filepath: str, coords=None) -> StructuredData:
    """Reader for seismic data stored in sgy/segy files

    Args:
        filepath (str): the path of the sgy/segy file
        coords (dict): If data is a numpy array coords provides the values for
         the xarray dimension. These dimensions are 'x', 'y' and 'z'

    Returns: a StructuredData object with data, the traces with samples written into an xr.Dataset, optionally with
     labels defined by coords

    """

    segyio = optional_requirements.require_segyio()
    segyfile = segyio.open(filepath, ignore_geometry=True)

    data = np.asarray([np.copy(tr) for tr in segyfile.trace[:]])

    sd = StructuredData.from_numpy(data)  # data holds traces * (samples per trace) values
    segyfile.close()
    return sd


def create_mesh_from_coords(coords: dict, zmin: Union[float, int], zmax: Union[float, int] = 0.0):
    """Creates a mesh for plotting StructuredData

    Args:
        coords (Union[dict, LineString]): the x and y, i.e. latitude and longitude, location of the traces of the seismic profile
        zmax (float): the maximum elevation of the seismic profile, by default 0.0
        zmin (float): the location in z where the lowest sample was taken

    Returns: vertices and faces for creating an UnstructuredData object

    """
    n = len(coords['x'])
    coords = np.array([coords['x'], coords['y']]).T
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

    scipy = optional_requirements.require_scipy()
    tri = scipy.spatial.qhull.Delaunay(vertices[:, [0, 2]])
    faces = tri.simplices
    return vertices, faces
