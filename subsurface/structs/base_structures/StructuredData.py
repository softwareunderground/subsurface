from dataclasses import dataclass
from typing import Dict, List

import numpy as np
import xarray as xr


@dataclass
class StructuredData:
    """Primary structure definition for structured data

       Check out other constructors: `StructuredData.from_numpy`,
        `StructuredData.from_data_array` and `StructuredData.from_dict`

    Args:
        data (xr.Dataset): object containing
         structured data, i.e. data that can be stored in multidimensional
         numpy array. The preferred type to pass as data is directly a
         xr.Dataset to be sure all the attributes are set and named as the user
         wants.
        data_array_name (str): If data is a numpy array or xarray DataArray, data_name
         provides the name for the xarray data variable
        coords (dict): If data is a numpy array coords provides the values for
         the xarray dimension. These dimensions are 'x', 'y' and 'z'

    Attributes:
        data (xarray.Dataset)
    """

    data: xr.Dataset

    def __init__(self, data_set: xr.Dataset, data_array_name="data_array"):
        if type(data_set) is not xr.Dataset:
            raise ValueError(
                "data_set must be a xarray.Dataset. See `from_numpy`, `from_data_array`"
                " and `from_dict` for other constructors ")

        self.data_array_name = data_array_name
        self.data = data_set

    @classmethod
    def from_numpy(cls, array: np.ndarray, coords: dict = None, data_array_name: str = "data_array",
                   coords_names: List[str] = None):
        if coords_names is None:
            if array.ndim == 2:
                cls.coord_names = ['x', 'y']
            elif array.ndim == 3:
                cls.coord_names = ['x', 'y', 'z']
            else:
                cls.coord_names = ['dim' + str(i) for i in range(array.ndim)]
        # if they are more than 3 we do not know the dimension name but it should
        # valid:
        return cls(xr.Dataset({data_array_name: (cls.coord_names, array)}, coords=coords), data_array_name)

    @classmethod
    def from_data_array(cls, data_array: xr.DataArray, data_array_name: str = "data_array"):
        return cls(xr.Dataset({data_array_name: data_array}), data_array_name)

    @classmethod
    def from_dict(cls, data_dict: Dict[str, xr.DataArray], coords: Dict[str, str] = None):
        return cls(xr.Dataset(data_vars=data_dict, coords=coords))

    @property
    def values(self):
        return self.data[self.data_array_name].values

    @property
    def default_dataset(self):
        return self.data[self.data_array_name]

    def to_binary(self, order='F'):
        bytearray_le = self._to_bytearray(order)
        header = self._set_binary_header()

        return bytearray_le, header

    def _set_binary_header(self):
        header = {"data_shape": self.values.shape}
        return header

    def _to_bytearray(self, order):
        data = self.values.astype('float32').tobytes(order)
        bytearray_le = data
        return bytearray_le
