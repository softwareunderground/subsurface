from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import xarray as xr

__all__ = ['StructuredData', ]


@dataclass(frozen=False)
class StructuredData:
    data: xr.Dataset
    _data_array_name: str = "data_array"

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
     
    Attributes:
        data (xarray.Dataset)
    """

    @property
    def data_array_name(self):
        data_var_list = list(self.data.data_vars.keys())
        if self._data_array_name not in data_var_list:
            raise ValueError("data_array_name not found in data_vars: {}".format(data_var_list))
        return self._data_array_name

    @data_array_name.setter
    def data_array_name(self, data_array_name: str):
        self._data_array_name = data_array_name

    @classmethod
    def from_numpy(cls, array: np.ndarray, coords: dict = None, data_array_name: str = "data_array",
                   dim_names: List[str] = None):
        if dim_names is None:
            if array.ndim == 2:
                dim_names = ['x', 'y']
            elif array.ndim == 3:
                dim_names = ['x', 'y', 'z']
            else:
                dim_names = ['dim' + str(i) for i in range(array.ndim)]
        # if they are more than 3 we do not know the dimension name but it should
        # valid:
        return cls(xr.Dataset({data_array_name: (dim_names, array)}, coords=coords), data_array_name)

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
    def default_data_array(self):
        return self.data[self.data_array_name]

    def default_data_array_to_binary(self, order='F'):
        bytearray_le = self._to_bytearray(self.default_data_array, order)
        header = self._set_binary_header(self.default_data_array)

        return bytearray_le, header
    
    def to_binary(self, data_array: xr.DataArray, order: str = 'F') -> Tuple[bytes, Dict]:
        bytearray_le = self._to_bytearray(data_array, order)
        header = self._set_binary_header(data_array)
        return bytearray_le, header
        
    @staticmethod
    def _set_binary_header(data_array: xr.DataArray) -> Dict:
        header = {"data_shape": data_array.shape}
        return header

    @staticmethod
    def _to_bytearray(data_array: xr.DataArray, order: str) -> bytes:
        data = data_array.values.astype('float32').tobytes(order)
        bytearray_le = data
        return bytearray_le
