"""For regularly gridded datasets like rasters and tensor meshes.

"""

import xarray as xr

from .common import Common


class GridData(Common):
    def __init__(self):
        self.ds = xr.Dataset()

    # Add pyvista methods of gridded data
