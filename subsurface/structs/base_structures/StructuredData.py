from dataclasses import dataclass
from typing import Union, Dict

import numpy as np
import xarray as xr


@dataclass
class StructuredData:
    """Primary structure definition for structured data

    Args:
        data (xr.Dataset, xr.DataArray, np.ndarray): object containing
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

    def __init__(
            self,
            data: Union[np.ndarray, xr.DataArray,
                        xr.Dataset, Dict[str, xr.DataArray]],
            data_array_name='data_array',
            coords: dict = None,
            coords_names=None
    ):

        self.data_array_name = data_array_name
        self.coord_names = coords_names

        if type(data) == xr.Dataset:
            self.data = data

        elif type(data) == dict:
            self.data = xr.Dataset(
                data_vars=data,
                coords=coords
            )
        elif type(data) == xr.DataArray:
            self.data = xr.Dataset({data_array_name: data})
        elif type(data) == np.ndarray:
            if coords_names is None:
                if data.ndim == 2:
                    self.coord_names = ['x', 'y']
                elif data.ndim == 3:
                    self.coord_names = ['x', 'y', 'z']
                else:
                    self.coord_names = ['dim' + str(i) for i in range(data.ndim)]

            # if they are more than 3 we do not know the dimension name but it should
            # valid:
            self.data = xr.Dataset(
                {data_array_name: (self.coord_names, data)},
                coords=coords
            )
        else:
            raise AttributeError(
                'data must be either xarray.Dataset, xarray.DataArray,'
                'or numpy.ndarray')

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
        header = {
            "data_shape": self.values.shape,
        }
        return header

    def _to_bytearray(self, order):
        data = self.values.astype('float32').tobytes(order)
        bytearray_le = data
        return bytearray_le