"""
TODO: This is legacy code waiting to be updated to the new ideas

"""

import xarray as xr
import segyio
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv


class Seismic:
    def __init__(self, data: np.ndarray, *args, **kwargs):
        """Seismic data object based on xarray.DataArray.
        
        Args:
            data (Array): np.ndarray of the seismic cube / section.
        """
        self.n_shp = len(data.shape)
        self._xarray = xr.DataArray(self._flip(data), *args, **kwargs)

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        return getattr(self._xarray, attr)
    
    def __getitem__(self, item):
        if isinstance(item, str):
            return self._xarray._getitem_coord(item)

        # preserve coordinates 
        cp = list(self._xarray.coords.items())  # parent coordinates
        coords = [(cp[i]) for i, it in enumerate(item) if not type(it) == int]
        return Seismic(self._xarray[item].data, coords=coords)
    
    def __repr__(self):
        return self._xarray.__repr__()
    
    def __str__(self):
        return "Seismic"

    def _flip(self, data: np.ndarray) -> np.ndarray:
        """Flip SEGY data to fit with numpy array orientation.

        Args:
            data (np.ndarray): Seismic data.

        Returns:
            (np.ndarray) Flipped seismic data.
        """
        if self.n_shp == 1:
            return data
        if self.n_shp == 2:
            return data
        if self.n_shp == 3:
            return np.flip(data, axis=2)

    def add_coords(self):
        """Ability to easily add physical coordinates."""
        raise NotImplementedError

    def to_segy(self, filepath: str) -> None:
        """Write given Seismic to SEGY file using segyio.tools.from_array().
        
        Args:
            filepath (str): Filepath for SEGY file.
        """
        segyio.tools.from_array(filepath, self._xarray.data)

    def plot_(self):
        return xr.plot.plot._PlotMethods(self)

    def plot(self):
        if self.n_shp == 1:
            return _plot_1d(self)
        elif self.n_shp == 2:
            pass
            # TODO: plot seismic section using imshow for correct orientation
        elif self.n_shp >= 3:
            _plot_3d(self)

    def create_pyvista_grid(self) -> pv.grid.UniformGrid:
        """Generate UniformGrid object for 3D plotting of the seismic.

        Args:
            seismic (Seismic): Seismic object.

        Returns:
            (pv.grid.UniformGrid)
        """
        grid = pv.UniformGrid()
        grid.spacing = (1, 1, 1)  # TODO: cell sizes? vertical exaggeration etc
        grid.dimensions = np.array(self.data.shape) + 1
        grid.cell_arrays["values"] = self.data.flatten(order="F")
        # TODO: correct orientation of cube
        return grid

    def plot_3d_slices(self):
        if self.n_shp != 3:
            raise AssertionError("Seismic data needs to be a 3-D volume.")
        # TODO: cmap, kwarg passthrough
        pv.OrthogonalSlicer(self.grid)


def _plot_1d(seismic: Seismic, linekwargs={}, fillkwargs={}):
    fig, ax = plt.subplots(figsize=(2,8))
    
    lkwargs = dict(
        color="black",
        linewidth=1
    )
    lkwargs.update(linekwargs)

    fkwargs = dict(
        color="grey"
    )
    fkwargs.update(fillkwargs)

    y = np.arange(0, *seismic.data.shape)
    ax.plot(seismic.data, y, **lkwargs)
    x1 = seismic.data.copy()
    x1[x1<=0] = 0
    ax.fill_betweenx(y, x1=x1, **fkwargs)
    return ax


def _plot_3d(seismic: Seismic):
    if not hasattr(seismic, "grid"):
        seismic.grid = seismic.create_pyvista_grid()

    seismic.grid.plot(cmap="seismic")


def _plot_2d(seismic: Seismic):
    pass


def _plot_hist(seismic: Seismic):
    pass
        

def from_segy(filepath:str, coords=None) -> Seismic:
    """Create a Seismic data object from a SEGY file.
    
    Args:
        filepath (str): Filepath to the SEGY file.
    
    Returns:
        Seismic: Seismic data object based on xarray.DataArray.
    """
    with segyio.open(filepath) as sf:
        sf.mmap()  # memory mapping
        xlines = sf.xlines
        ilines = sf.ilines
        samples = sf.samples
        header = sf.bin

    if not coords:
        coords = [
            ("ilines", ilines), 
            ("xlines", xlines),
            ("samples", samples)
        ]

    cube = segyio.tools.cube(filepath)
    seismic = Seismic(cube, coords=coords)
    seismic.header = header
    return seismic
