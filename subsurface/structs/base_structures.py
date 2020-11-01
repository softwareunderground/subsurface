import pathlib
from dataclasses import dataclass
from typing import Union, Optional, Dict

import numpy as np
import pandas as pd
import xarray as xr


@dataclass
class UnstructuredData:
    """Primary structure definition for unstructured data

    Attributes:
        data (`xarray.Dataset`): Data structure where we store

    Args:
        vertex (np.ndarray): NDArray[(Any, 3), FloatX]: XYZ point data
        edges (np.ndarray): NDArray[(Any, ...), IntX]: Combination of vertex that create
            different geometric elements
        attributes (pd.DataFrame): NDArray[(Any, ...), FloatX]: Number associated to an element
        points_attributes (pd.DataFrame): NDArray[(Any, ...), FloatX]: Number
         associated to points

    Notes:
        Depending on the shape of `edge` the following unstructured elements can be create:
        - edges NDArray[(Any, 0), IntX] or NDArray[(Any, 1), IntX] -> *Point cloud*.
         E.g. Outcrop scan with lidar
        - edges NDArray[(Any, 2), IntX] -> *Lines*. E.g. Borehole
        - edges NDArray[(Any, 3), IntX] -> *Mesh*. E.g surface-DEM Topography
        - edges NDArray[(Any, 4), IntX]
            - -> *tetrahedron*
            - -> *quadrilateral (or tetragon)* UNSUPPORTED?
        - edges NDArray[(Any, 8), IntX] -> *Hexahedron: Unstructured grid/Prisms*

    """
    data: xr.Dataset

    def __init__(self, vertex: np.ndarray, edges: np.ndarray = None,
                 attributes: Optional[
                     Union[pd.DataFrame, Dict[str, xr.DataArray]]] = None,
                 points_attributes: Optional[pd.DataFrame] = None):

        self.attributes_name = 'attributes'
        self.points_attributes_name = 'points_attributes'

        xarray_dict = dict()

        v = xr.DataArray(vertex,
                         dims=['points', 'XYZ'],
                         coords={'XYZ': ['X', 'Y', 'Z']}
                         )
        xarray_dict['vertex'] = v

        if edges is None:
            edges = np.atleast_2d(v.coords['points'])

        e = xr.DataArray(edges, dims=['edge', 'nodes'])
        xarray_dict['edges'] = e

        xarray_dict = self.set_attributes_data_array(
            attributes,
            edges.shape[0],
            xarray_dict,
            dims=['edge', 'attribute'],
            attributes_type=self.attributes_name
        )
        xarray_dict = self.set_attributes_data_array(
            points_attributes,
            vertex.shape[0],
            xarray_dict,
            dims=['points',
                  'points_attribute'],
            attributes_type=self.points_attributes_name
        )
        self.data = xr.Dataset(xarray_dict)

        try:
            self.data = self.data.reset_index('edge')
        except KeyError:
            pass

        self.validate()

    def set_attributes_data_array(self, attributes, n_item, xarray_dict, dims,
                                  attributes_type):
        if attributes is None:
            attributes = pd.DataFrame(np.zeros((n_item, 0)))
        if type(attributes) is pd.DataFrame:
            a = xr.DataArray(attributes, dims=dims)
            xarray_dict[attributes_type] = a
        elif type(attributes) is dict:
            x_attr = self.set_attributes_for_dicts(attributes,
                                                   attributes_type,
                                                   xarray_dict)
            xarray_dict = {**xarray_dict, **x_attr}

        return xarray_dict

    def set_attributes_for_dicts(self, attributes, attributes_type, xarray_dict):
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
    def edges(self):
        return self.data['edges'].values

    @edges.setter
    def edges(self, array):
        self.data['edges'] = xr.DataArray(array, dims=['e', 'nodes'])

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
        return self.edges.shape[0]

    @property
    def n_vertex_per_element(self):
        return self.edges.shape[1]

    @property
    def n_points(self):
        return self.vertex.shape[0]

    @property
    def attributes_to_dict(self, orient='list'):
        return self.attributes.to_dict(orient)

    @property
    def points_attributes_to_dict(self, orient='list'):
        return self.points_attributes_to_dict.to_dict(orient)

    def validate(self):
        """Make sure the number of vertices matches the associated data."""
        if self.data['edges'].shape[0] != self.data[self.attributes_name].shape[0]:
            raise AttributeError('Attributes and edges must have the same length.')

    def to_xarray(self):
        a = xr.DataArray(self.vertex, dims=['points', 'XYZ'])
        b = xr.DataArray(self.edges, dims=['edges', 'node'])
        e = xr.DataArray(self.attributes, dims=['element', 'attribute'])
        c = xr.Dataset({'v': a, 'e': b, 'a': e})
        return c

    def to_disk(self, file: str = None, **kwargs):
        return self.data.to_netcdf(file, **kwargs)


@dataclass
class StructuredData:
    """Primary structure definition for structured data

    Args:
        data (xr.Dataset, xr.DataArray, np.ndarray): object containing
         structured data, i.e. data that can be stored in multidimensional
          numpy array. The preferred type to pass as data is directly a
         xr.Dataset to be sure all the attributes are set and named as the user
         wants.
        data_name (str): If data is a numpy array or xarray DataArray, data_name
         provides the name for the xarray data variable
        coords (dict): If data is a numpy array coords provides the values for
         the xarray dimension. These dimensions are 'x', 'y' and 'z'

    Attributes:
        data (xr.Dataset)

    """

    data: xr.Dataset

    def __init__(
            self,
            data: Union[
                np.ndarray, xr.DataArray, xr.Dataset, Dict[str, xr.DataArray]],
            data_name: str = 'data',
            coords: dict = None
    ):

        if type(data) == xr.Dataset:
            self.data = data

        elif type(data) == list:
            self.data = xr.Dataset(
                data_vars=data,
                coords=coords
            )

        elif type(data) == xr.DataArray:
            self.data = xr.Dataset({data_name: data})
        elif type(data) == np.ndarray:
            if data.ndim == 2:
                self.data = xr.Dataset(
                    {data_name: (['x', 'y'], data)},
                    coords=coords
                )
            elif data.ndim == 3:
                self.data = xr.Dataset(
                    {data_name: (['x', 'y', 'z'], data)},
                    coords=coords
                )
        else:
            AttributeError('data must be either xarray.Dataset, xarray.DataArray,'
                           'or numpy.ndarray')
