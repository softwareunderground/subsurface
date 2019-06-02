# Copyright (c) 2019 Subsurface Developers, where applicable.
# Copyright (c) 2018 MetPy Developers, where applicable.
# Distributed under the terms of the BSD 3-Clause License.
# SPDX-License-Identifier: BSD-3-Clause

"""Accessors to provide basic functions for Subsurface objects."""

import functools

import xarray as xr

from xarray.core.accessors import DatetimeAccessor
from xarray.core.indexing import expanded_indexer
from xarray.core.utils import either_dict_or_kwargs, is_dict_like

from .units import DimensionalityError, units

@xr.register_dataarray_accessor('subsurface')
class SubsurfaceAccessor(object):
    """Provide custom attributes and methods on XArray DataArray for Subsurface functionality."""

    def __init__(self, data_array):
        """Initialize accessor with a DataArray."""
        self._data_array = data_array
        self._units = self._data_array.attrs.get('units', 'dimensionless')

    @property
    def units(self):
        return units(self._units)

    @property
    def unit_array(self):
        """Return data values as a `pint.Quantity`."""
        return self._data_array.values * self.units

    @unit_array.setter
    def unit_array(self, values):
        """Set data values as a `pint.Quantity`."""
        self._data_array.values = values
        self._units = self._data_array.attrs['units'] = str(values.units)

    def convert_units(self, units):
        """Convert the data values to different units in-place."""
        self.unit_array = self.unit_array.to(units)
    

    def set_units(self, units):
        """Set the data values to different units in-place."""
        self._units = self._data_array.attrs['units'] = str(units)

    @property
    def crs(self):
        """Provide easy access to the `crs` coordinate."""
        if 'crs' in self._data_array.coords:
            return self._data_array.coords['crs'].item()
        raise AttributeError('crs attribute is not available.')

    @property
    def cartopy_crs(self):
        """Return the coordinate reference system (CRS) as a cartopy object."""
        return self.crs.to_cartopy()

    #def _axis(self, axis):
    #    """Return the coordinate variable corresponding to the given individual axis type."""
    #    if axis in readable_to_cf_axes:
    #        for coord_var in self._data_array.coords.values():
    #           if coord_var.attrs.get('_metpy_axis') == readable_to_cf_axes[axis]:
    #                return coord_var
    #        raise AttributeError(axis + ' attribute is not available.')
    #    else:
    #        raise AttributeError("'" + axis + "' is not an interpretable axis.")


    def coordinates(self, *args):
        """Return the coordinate variables corresponding to the given axes types."""
        for arg in args:
            yield self._axis(arg)

    #@property
    #def time(self):
    #    return self._axis('time')

    #@property
    #def vertical(self):
    #    return self._axis('vertical')

    #@property
    #def y(self):
    #    return self._axis('y')

    #@property
    #def x(self):
    #    return self._axis('x')

    def coordinates_identical(self, other):
        """Return whether or not the coordinates of other match this DataArray's."""
        # If the number of coordinates do not match, we know they can't match.
        if len(self._data_array.coords) != len(other.coords):
            return False

        # If same length, iterate over all of them and check
        for coord_name, coord_var in self._data_array.coords.items():
            if coord_name not in other.coords or not other[coord_name].identical(coord_var):
                return False

        # Otherwise, they match.
        return True

    def find_axis_name(self, axis):
        """Return the name of the axis corresponding to the given identifier.
        The given indentifer can be an axis number (integer), dimension coordinate name
        (string) or a standard axis type (string).
        """
        if isinstance(axis, int):
            # If an integer, use the corresponding dimension
            return self._data_array.dims[axis]
        elif axis not in self._data_array.dims and axis in readable_to_cf_axes:
            # If not a dimension name itself, but a valid axis type, get the name of the
            # coordinate corresponding to that axis type
            return self._axis(axis).name
        elif axis in self._data_array.dims and axis in self._data_array.coords:
            # If this is a dimension coordinate name, use it directly
            return axis
        else:
            # Otherwise, not valid
            raise ValueError('Given axis is not valid. Must be an axis number, a dimension '
                             'coordinate name, or a standard axis type.')

    class _LocIndexer(object):
        """Provide the unit-wrapped .loc indexer for data arrays."""

        def __init__(self, data_array):
            self.data_array = data_array
        
        def expand(self, key):
            """Parse key using xarray utils to ensure we have dimension names."""
            if not is_dict_like(key):
                labels = expanded_indexer(key, self.data_array.ndim)
                key = dict(zip(self.data_array.dims, labels))
            return key

        def __getitem__(self, key):
            key = _reassign_quantity_indexer(self.data_array, self.expand(key))
            return self.data_array.loc[key]

        def __setitem__(self, key, value):
            key = _reassign_quantity_indexer(self.data_array, self.expand(key))
            self.data_array.loc[key] = value

    @property
    def loc(self):
        """Make the LocIndexer available as a property."""
        dtype = type(self)
        return dtype(self._LocIndexer(self._data_array))

    def sel(self, indexers=None, method=None, tolerance=None, drop=False, **indexers_kwargs):
        """Wrap DataArray.sel to handle units."""
        dtype = type(self)
        indexers = either_dict_or_kwargs(indexers, indexers_kwargs, 'sel')
        indexers = _reassign_quantity_indexer(self._data_array, indexers)
        return dtype(self._data_array.sel(indexers, method=method, tolerance=tolerance, drop=drop))
        


def _reassign_quantity_indexer(data, indexers):
    """Reassign a units.Quantity indexer to units of relevant coordinate."""
    def _to_magnitude(val, unit):
        try:
            return val.to(unit).m
        except AttributeError:
            return val

    for coord_name in indexers:
        # Handle axis types for DataArrays
        if (isinstance(data, xr.DataArray) and coord_name not in data.dims
                and coord_name in readable_to_cf_axes):
            axis = coord_name
            coord_name = next(data.subsurface.coordinates(axis)).name
            indexers[coord_name] = indexers[axis]
            del indexers[axis]

        # Handle slices of quantities
        if isinstance(indexers[coord_name], slice):
            start = _to_magnitude(indexers[coord_name].start, data[coord_name].subsurface.units)
            stop = _to_magnitude(indexers[coord_name].stop, data[coord_name].subsurface.units)
            step = _to_magnitude(indexers[coord_name].step, data[coord_name].subsurface.units)
            indexers[coord_name] = slice(start, stop, step)

        # Handle quantities
        indexers[coord_name] = _to_magnitude(indexers[coord_name],
                                             data[coord_name].subsurface.units)

    return indexers

def check_matching_coordinates(func):
    """Decorate a function to make sure all given DataArrays have matching coordinates."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        data_arrays = ([a for a in args if isinstance(a, xr.DataArray)]
                       + [a for a in kwargs.values() if isinstance(a, xr.DataArray)])
        if len(data_arrays) > 1:
            first = data_arrays[0]
            for other in data_arrays[1:]:
                if not first.subsurface.coordinates_identical(other):
                    raise ValueError('Input DataArray arguments must be on same coordinates.')
        return func(*args, **kwargs)
    return wrapper

def preprocess_xarray(func):
    """Decorate a function to convert all DataArray arguments to pint.Quantities.
    This uses the subsurface xarray accessors to do the actual conversion.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args = tuple(a.subsurface.unit_array if isinstance(a, xr.DataArray) else a for a in args)
        kwargs = {name: (v.subsurface.unit_array if isinstance(v, xr.DataArray) else v)
                  for name, v in kwargs.items()}
        return func(*args, **kwargs)
    return wrapper