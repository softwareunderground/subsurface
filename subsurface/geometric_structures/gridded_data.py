import xarray as xr


class GridData:
    def __init__(self):
        self.ds = xr.Dataset()

    # Add pyvista methods of gridded data
