# import rasterio

from pathlib import Path
import ezdxf
import numpy as np
from scipy.spatial.qhull import Delaunay

from subsurface import UnstructuredData


def read_topography(path) -> UnstructuredData:
    extension = get_extension(path)
    if extension == '.dxf':
        faces, vertex = dxf_to_vertex_edges(path)
    else:
        raise NotImplementedError('The extension given cannot be read yet')

    unstruct = UnstructuredData(vertex, faces)
    return unstruct


def dxf_to_vertex_edges(path):
    dataset = ezdxf.readfile(path)
    vertex = []
    entity = dataset.modelspace()
    for e in entity:
        vertex.append(e[0])
        vertex.append(e[1])
        vertex.append(e[2])
    vertex = np.array(vertex)
    vertex = np.unique(vertex, axis=0)
    tri = Delaunay(vertex[:, [0, 1]])
    faces = tri.simplices
    return faces, vertex


def get_extension(path):
    p = Path(path)
    return p.suffix
