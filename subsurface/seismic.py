# Copyright (c) 2018 MetPy Developers.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

import xarray as xr
from nptyping import Array
import segyio
import matplotlib.pyplot as plt

import numpy as np

from .xarray import *
from .xarray import _reassign_quantity_indexer

class Seismic(xr.DataArray):
    def __init__(self, data: Array, units='dimensionless', *args, **kwargs):
        """Seismic data object based on xarray.DataArray.
        
        Args:
            data (Array): np.ndarray of the seismic cube / section.
        """
        self._xarray = xr.DataArray(data, *args, **kwargs)
        self._units = self._xarray.attrs.get('units', units)    
        self.n_shp = len(self._xarray.data.shape)
        
    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self, attr)
        try:
            return getattr(self._xarray.subsurface, attr)
        except:
            return getattr(self._xarray, attr)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._xarray._getitem_coord(item)

        # preserve coordinates 
        cp = list(self._xarray.coords.items())  # parent coordinates
        coords = [(cp[i]) for i, it in enumerate(item) if not type(it) == int]
        nits = self._units
        return Seismic(self._xarray[item].data, coords=coords, units=nits)
    
    def __repr__(self):
        return self._xarray.__repr__()
    
    def __str__(self):
        return "Seismic"

    def to_segy(self, filepath: str) -> None:
        """Write given Seismic to SEGY file using segyio.tools.from_array().
        
        Args:
            filepath (str): Filepath for SEGY file.
        """
        segyio.tools.from_array(filepath, self._xarray.data)

    @property
    def plot(self):
        return xr.plot.plot._PlotMethods(self)
    
    # End of MetPy Code.

def from_segy(filepath:str, coords=None, units='dimensionless') -> Seismic:
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
    seismic = Seismic(cube, coords=coords, units=units)
    seismic.header = header
    return seismic
