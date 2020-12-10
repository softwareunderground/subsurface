from typing import Union
import numpy as np
from scipy.spatial.qhull import Delaunay
from shapely.geometry import LineString


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
