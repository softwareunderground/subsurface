import rasterio
import ezdxf
import numpy as np
from scipy.spatial.qhull import Delaunay

from subsurface import UnstructuredData, StructuredData
from subsurface.utils import get_extension


def read_structured_topography(path) -> StructuredData:
    extension = get_extension(path)
    if extension == '.tif':
        dataset = rasterio.open(path)
        structured_data = rasterio_dataset_to_structured_data(dataset)
    else:
        raise NotImplementedError('The extension given cannot be read yet')

    return structured_data


def rasterio_dataset_to_structured_data(dataset):
    data = dataset.read(1)
    shape = data.shape
    coords = {
        'x': np.linspace(
            dataset.bounds.left,
            dataset.bounds.right,
            shape[0]
        ),
        'y': np.linspace(
            dataset.bounds.bottom,
            dataset.bounds.top,
            shape[1]
        )
    }
    structured_data = StructuredData(data=data, coords=coords,
                                     data_name='topography')
    return structured_data


def read_unstructured_topography(path) -> UnstructuredData:
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



