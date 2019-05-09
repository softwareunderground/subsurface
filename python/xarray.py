""" 
Provides functionality to access xarray as underlying datastructure for subsurface.
"""
import xarray as xr
from xarray.core.accessors import DatetimeAccessor
from xarray.core.indexing import expanded_indexer
from xarray.core.utils import either_dict_or_kwargs, is_dict_like