import xarray as xr
from nptyping import Array

import numpy as np

from .units import DimensionalityError, units

class Seismic:
    def __init__(self, data: Array, *args, **kwargs):
        """Seismic data object based on xarray.DataArray.
        
        Args:
            data (Array): np.ndarray of the seismic cube / section.
        """
        self._xarray = xr.DataArray(data, *args, **kwargs)
        self._units = self._xarray.attrs.get('units', 'dimensionless')
        
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

    def copy(self):
        """Deep copy file."""
        raise NotImplementedError

    def __repr__(self):
        return self._xarray.__repr__()
    
    def __str__(self):
        return "Seismic"

    def add_coords(self):
        """Ability to easily add physical coordinates."""
        raise NotImplementedError

    def to_segy(self):
        """Write to SEGY file."""
        raise NotImplementedError

    @property
    def plot(self):
        return xr.plot.plot._PlotMethods(self)

    @property
    def units(self):
        return units(self._units)

    @property
    def unit_array(self):
        """Return data values as a `pint.Quantity`."""
        return self._xarray.values * self.units
    
    @unit_array.setter
    def unit_array(self, values):
        """Set data values as a `pint.Quantity`."""
        self._xarray.values = values
        self._units = self._xarray.attrs['units'] = str(values.units)

    def convert_units(self, units):
        """Convert the data values to different units in-place."""
        self.unit_array = self.unit_array.to(units)
    
    def set_units(self, units):
        """Set the data values to different units in-place."""
        self._units = self._xarray.attrs['units'] = str(units)
