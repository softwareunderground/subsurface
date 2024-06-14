from typing import Sequence, Optional

import numpy as np

from ....core.structs.structured_elements.structured_grid import StructuredGrid
from ....optional_requirements import require_rasterio
from ....core.structs import StructuredData, UnstructuredData
from ....core.utils.utils_core import get_extension
from ....core.reader_helpers.readers_data import GenericReaderFilesHelper
from ....core.reader_helpers.reader_unstruct import ReaderUnstructuredHelper
from ..mesh.surfaces_api import read_2d_mesh_to_unstruct


def read_structured_topography(path, crop_to_extent: Optional[Sequence]=None) -> StructuredData:
    rasterio = require_rasterio()

    extension = get_extension(path)
    if extension == '.tif':
        structured_data = rasterio_dataset_to_structured_data(
            dataset=rasterio.open(path),
            crop_to_extent=crop_to_extent
        )
        
    else:
        raise NotImplementedError('The extension given cannot be read yet')

    return structured_data


def read_structured_topography_to_unstructured(path) -> UnstructuredData:
    structured_data = read_structured_topography(path)
    return topography_to_unstructured_data(structured_data)


def rasterio_dataset_to_structured_data(dataset, crop_to_extent: Optional[Sequence]=None):
    if crop_to_extent is not None: 
        window = _get_raster_window(crop_to_extent, dataset)
    else:
        window = None

    data = dataset.read(1, window=window)
    data = np.fliplr(data.T)
    shape = data.shape
    
    # TODO: ===================
    # TODO: Add the option to crop
    # TODO: Resample
    
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
    structured_data = StructuredData.from_numpy(data, data_array_name='topography', coords=coords)
    return structured_data


def read_unstructured_topography(path) -> UnstructuredData:
    return read_2d_mesh_to_unstruct(ReaderUnstructuredHelper(GenericReaderFilesHelper(path)))


def topography_to_unstructured_data(structured_data: StructuredData) -> UnstructuredData:
    from subsurface.modules.visualization import to_pyvista_grid

    sg = StructuredGrid(structured_data)
    s = to_pyvista_grid(sg, data_order='C', data_set_name='topography')
    un_s = s.cast_to_unstructured_grid()
    un_s.triangulate(inplace=True)
    vertex = un_s.points
    cells = un_s.cells.reshape(-1, 4)[:, 1:]

    unstructured_data = UnstructuredData.from_array(vertex, cells)
    return unstructured_data


def _get_raster_window(crop_to_extent, dataset):
    from rasterio.windows import Window
    # TODO: Add None check
    # Get the indices of the window
    left, bottom, right, top = crop_to_extent
    row_start, col_start = dataset.index(left, top)
    row_stop, col_stop = dataset.index(right, bottom)
    # Read the data in the window
    window = Window.from_slices((row_start, row_stop), (col_start, col_stop))
    return window
