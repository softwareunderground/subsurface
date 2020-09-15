"""For regularly gridded datasets like rasters and tensor meshes.

"""

import xarray as xr

from .common import Common
from .primary_structures import StructuredData


class StructuredSurface(Common):
    def __init__(self, structured_data: StructuredData):
        # TODO check structured_data has two coordinates
        self.ds = structured_data

    # Add pyvista methods of gridded data


class StructuredGrid(Common):
    # TODO check structured_data has three coordinates
    def __init__(self, structured_data: StructuredData):
        self.ds = structured_data
