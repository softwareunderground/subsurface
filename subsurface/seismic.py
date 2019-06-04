import xarray as xr
from nptyping import Array
import segyio
import matplotlib.pyplot as plt


class Seismic:
    def __init__(self, data: Array, *args, **kwargs):
        """Seismic data object based on xarray.DataArray.
        
        Args:
            data (Array): np.ndarray of the seismic cube / section.
        """
        self._xarray = xr.DataArray(data, *args, **kwargs)
        self.n_shp = len(self._xarray.data.shape)
        
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

    def add_coords(self):
        """Ability to easily add physical coordinates."""
        raise NotImplementedError

    def to_segy(self, filepath: str) -> None:
        """Write given Seismic to SEGY file using segyio.tools.from_array().
        
        Args:
            filepath (str): Filepath for SEGY file.
        """
        segyio.tools.from_array(filepath, self._xarray.data)

    @property
    def plot(self):
        return xr.plot.plot._PlotMethods(self)

    @property
    def plot_(self):
        if self.n_shp == 1:
            # TODO: plot seismic trace as wiggle plot
            return _plot_1d(self)
        elif self.n_shp == 2:
            # TODO: plot seismic section using imshow
        elif self.n_shp >= 3:
            # TODO: plot seismic as hist


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
