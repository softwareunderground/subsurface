import os
import pathlib
from dataclasses import dataclass
from typing import Union, Optional, Dict, List

import numpy as np
import pandas as pd
import xarray as xr


class CommonDataMethods:
    def __init__(self):
        self.data = None

    @staticmethod
    def default_path_and_name(path, name='subsurface_data.nc', ):
        if not path:
            path = './'
        if os.path.isdir(path):
            print("Directory already exists, files will be overwritten")
        else:
            os.makedirs(f'{path}')
        path = f'{path}/{name}'
        return name, path

    def to_netcdf(self, path=None, file: str = None, **kwargs):
        if path is None and file is not None:
            name, path = self.default_path_and_name(path, file)
        return self.data.to_netcdf(path, **kwargs)

    def replace_outliers(self, dim=0, perc=0.99, replace_for=None):
        """@Edoardo Guerreiro https://stackoverflow.com/questions/60816533/
         is-there-a-built-in-function-in-xarray-to-remove-outliers-from-a-dataset"""

        data = self.data
        # calculate percentile
        threshold = data[dim].quantile(perc)

        # find outliers and replace them with max among remaining values
        mask = data[dim].where(abs(data[dim]) <= threshold)
        if replace_for == 'max':
            max_value = mask.max().values
            # .where replace outliers with nan
            mask = mask.fillna(max_value)
        elif replace_for == 'min':
            min_value = mask.min().values
            # .where replace outliers with nan
            mask = mask.fillna(min_value)

        print(mask)
        data[dim] = mask

        return data


@dataclass
class UnstructuredData(CommonDataMethods):
    """Primary structure definition for unstructured data

    Attributes:
        data (`xarray.Dataset`): Data structure where we store

    Args:
        vertex (np.ndarray): NDArray[(Any, 3), FloatX]: XYZ point data
        cells (np.ndarray, str['points', 'line']): NDArray[(Any, ...), IntX]:
         Combination of vertex that create different geometric elements. If
         str use default values for either points or lines
        attributes (pd.DataFrame): NDArray[(Any, ...), FloatX]: Number associated to an element
        points_attributes (pd.DataFrame): NDArray[(Any, ...), FloatX]: Number
         associated to points
        ds (xarray.Dataset): Directly a dataset with the expected structured. This
         arg is specially thought for loading data from disk

    Notes:
        Depending on the shape of `edge` the following unstructured elements can
        be created:

        - cells NDArray[(Any, 0), IntX] or NDArray[(Any, 1), IntX] -> *Point cloud*.
          E.g. Outcrop scan with lidar
        - cells NDArray[(Any, 2), IntX] -> *Lines*. E.g. Borehole
        - cells NDArray[(Any, 3), IntX] -> *Mesh*. E.g surface-DEM Topography
        - cells NDArray[(Any, 4), IntX]
           - -> *tetrahedron*
           - -> *quadrilateral (or tetragon)* UNSUPPORTED?
        - cells NDArray[(Any, 8), IntX] -> *Hexahedron: Unstructured grid/Prisms*
    """

    def __init__(self,
                 vertex: np.ndarray = None,
                 cells: Union[np.ndarray, str] = None,
                 attributes: Optional[Union[pd.DataFrame, Dict[str, xr.DataArray]]] = None,
                 points_attributes: Optional[pd.DataFrame] = None,
                 coords=None,
                 ds=None,
                 xarray_attributes: Optional[dict] = None):

        super().__init__()
        self.attributes_name = 'attributes'
        self.points_attributes_name = 'points_attributes'

        if vertex is None and ds is None:
            raise AttributeError('Either vertex or ds must be passed.')

        if ds is None:
            ds = self._create_dataset_from_numpy(vertex, cells, attributes, points_attributes,
                                                 coords, xarray_attributes)
        self.data = ds

        try:
            self.data = self.data.reset_index('cell')
        except KeyError:
            pass

        self._validate()

    def _create_dataset_from_numpy(self, vertex, edges, attributes, points_attributes,
                                   coords, xarray_attributes):
        # ---- vertex DataArray
        xarray_dict = dict()
        v = xr.DataArray(vertex, dims=['points', 'XYZ'],
                         coords={'XYZ': ['X', 'Y', 'Z']})
        xarray_dict['vertex'] = v
        # ---- edges/cells DataArray
        if edges is None or edges == 'points':
            edges = np.atleast_2d(v.coords['points']).T
        elif edges == 'lines':
            n_vertex = v.coords['points'].shape[0]
            a = np.arange(0, n_vertex - 1, dtype=np.int_)
            b = np.arange(1, n_vertex, dtype=np.int_)
            edges = np.vstack([a, b]).T

        e = xr.DataArray(edges, dims=['cell', 'nodes'])
        xarray_dict['cells'] = e
        # ---- Attr DataArray

        xarray_dict = self.set_attributes_data_array(
            attributes,
            edges.shape[0],
            xarray_dict,
            dims=['cell', 'attribute'],
            attributes_type=self.attributes_name
        )
        # ---- Point Attr DataArray
        xarray_dict = self.set_attributes_data_array(
            points_attributes,
            vertex.shape[0],
            xarray_dict,
            dims=['points', 'points_attribute'],
            attributes_type=self.points_attributes_name
        )

        ds = xr.Dataset(xarray_dict, coords=coords, attrs=xarray_attributes)
        return ds

    def _validate(self):
        try:
            _ = self.data[self.attributes_name]['cell']
            _ = self.data[self.attributes_name]['attribute']

        except KeyError:
            raise KeyError('Attributes DataArrays must contain dimension cell and '
                           'attribute')
        """Make sure the number of vertices matches the associated data."""
        try:
            _ = self.data[self.points_attributes_name]['points_attribute']
            _ = self.data[self.points_attributes_name]['points']
        except KeyError:
            raise KeyError('Point Attribute DataArrays must contain dimensions'
                           ' points and points_attribute.')

        if self.data['cells']['cell'].size != self.data[self.attributes_name][
            'cell'].size:
            raise AttributeError('Attributes and cells must have the same length.')

    def set_attributes_data_array(self, attributes, n_item, xarray_dict, dims,
                                  attributes_type):
        if attributes is None:
            attributes = pd.DataFrame(np.zeros((n_item, 0)))
        if type(attributes) is pd.DataFrame:
            a = xr.DataArray(attributes, dims=dims)
            xarray_dict[attributes_type] = a
        elif type(attributes) is dict:
            x_attr = self.set_attributes_names_from_dicts(attributes,
                                                          attributes_type,
                                                          xarray_dict)
            xarray_dict = {**xarray_dict, **x_attr}

        return xarray_dict

    def set_attributes_names_from_dicts(self, attributes, attributes_type,
                                        xarray_dict):
        new_default_name = attributes.get(attributes_type, next(iter(attributes)))
        if attributes_type == self.attributes_name:
            self.attributes_name = new_default_name
        elif attributes_type == self.points_attributes_name:
            self.points_attributes_name = new_default_name
        xarray_dict = {**xarray_dict, **attributes}
        return xarray_dict

    @property
    def vertex(self):
        return self.data['vertex'].values

    @vertex.setter
    def vertex(self, array):
        self.vertex = xr.DataArray(array, dims=['points', 'XYZ'])

    @property
    def cells(self):
        return self.data['cells'].values

    @cells.setter
    def cells(self, array):
        self.data['cells'] = xr.DataArray(array, dims=['e', 'nodes'])

    @property
    def attributes(self):
        xarray = self.data[self.attributes_name]
        return xarray.to_dataframe()[self.attributes_name].unstack(level=1)

    @attributes.setter
    def attributes(self, dataframe):
        self.data[self.attributes_name] = xr.DataArray(dataframe,
                                                       dims=['element', 'attribute'])

    @property
    def points_attributes(self):
        return self.data[self.points_attributes_name].to_dataframe()[
            self.points_attributes_name].unstack(level=1)

    @points_attributes.setter
    def points_attributes(self, dataframe):
        self.data[self.points_attributes_name] = xr.DataArray(dataframe,
                                                              dims=['points',
                                                                    'points_attribute'])

    @property
    def n_elements(self):
        return self.cells.shape[0]

    @property
    def n_vertex_per_element(self):
        return self.cells.shape[1]

    @property
    def n_points(self):
        return self.vertex.shape[0]

    @property
    def attributes_to_dict(self, orient='list'):
        return self.attributes.to_dict(orient)

    @property
    def points_attributes_to_dict(self, orient='list'):
        return self.points_attributes_to_dict.to_dict(orient)

    def to_xarray(self):
        a = xr.DataArray(self.vertex, dims=['points', 'XYZ'])
        b = xr.DataArray(self.cells, dims=['cells', 'node'])
        e = xr.DataArray(self.attributes, dims=['element', 'attribute'])
        c = xr.Dataset({'v': a, 'e': b, 'a': e})
        return c

    def to_binary(self, order='F'):
        bytearray_le = self._to_bytearray(order)
        header = self._set_binary_header()

        return bytearray_le, header

    def _set_binary_header(self):

        header = {
            "vertex_shape": self.vertex.shape,
            "cell_shape": self.cells.shape,
            "cell_attr_shape": self.attributes.shape,
            "vertex_attr_shape": self.points_attributes.shape,
            "cell_attr_names": self.attributes.columns.to_list(),
            "cell_attr_types": self.attributes.dtypes.astype(str).to_list(),
            "vertex_attr_names": self.points_attributes.columns.to_list(),
            "vertex_attr_types": self.attributes.dtypes.astype(str).to_list(),
            "xarray_attrs": self.data.attrs
        }
        return header

    def _to_bytearray(self, order):
        vertex = self.vertex.astype('float32').tobytes(order)
        cells = self.cells.astype('int32').tobytes(order)
        cell_attribute = self.attributes.values.astype('float32').tobytes(order)
        vertex_attribute = self.points_attributes.values.astype('float32').tobytes(
            order)
        bytearray_le = vertex + cells + cell_attribute + vertex_attribute
        return bytearray_le


@dataclass
class StructuredData(CommonDataMethods):
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
