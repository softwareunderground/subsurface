import numpy as np

from subsurface.reader.readers_data import ReaderFilesHelper, ReaderUnstructuredHelper
from subsurface.structs import StructuredData, UnstructuredData
from subsurface.reader.mesh.surfaces_api import read_2d_mesh_to_unstruct
from subsurface.utils.utils_core import get_extension


__all__ = ['read_structured_topography', 'rasterio_dataset_to_structured_data',
           'read_unstructured_topography']


def read_structured_topography(path) -> StructuredData:
    import rasterio

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
            dataset.bounds.right,
            dataset.bounds.left,
            shape[0]
        ),
        'y': np.linspace(
            dataset.bounds.bottom,
            dataset.bounds.top,
            shape[1]
        )
    }
    structured_data = StructuredData.from_numpy(data, data_array_name='topography',
                                                coords=coords)
    return structured_data


def read_unstructured_topography(path) -> UnstructuredData:
    return read_2d_mesh_to_unstruct(ReaderUnstructuredHelper(ReaderFilesHelper(path)))
