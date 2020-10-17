import pathlib
from dataclasses import dataclass
from typing import Union, Optional

import numpy as np
import pandas as pd
import xarray as xr


@dataclass
class UnstructuredData:
    """Primary structure definition for unstructured data

    Attributes:
        vertex (np.ndarray): NDArray[(Any, 3), FloatX]: XYZ point data
        edges (np.ndarray): NDArray[(Any, ...), IntX]: Combination of vertex that create
            different geometric elements
        attributes (pd.DataFrame): NDArray[(Any, ...), FloatX]: Number associated to an element

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
    #vertex: np.ndarray
    #edges: np.ndarray
    #attributes: Optional[pd.DataFrame] = None

    def __init__(self, vertex: np.ndarray, edges: np.ndarray,
                 attributes: Optional[pd.DataFrame] = None):
        v = xr.DataArray(vertex, dims=['points', 'XYZ'])
        e = xr.DataArray(edges, dims=['edge', 'nodes'])

        if attributes is None:
            attributes = pd.DataFrame(np.zeros((edges.shape[0], 0)))

        a = xr.DataArray(attributes, dims=['element', 'attribute'])
        c = xr.Dataset({'vertex': v, 'edges': e, 'attributes': a})
        self.data = c.reset_index('element')

        self.validate()


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
        return self.data['attributes'].to_dataframe()['attributes'].unstack(level=1)

    @attributes.setter
    def attributes(self, dataframe):
        self.data['attributes'] = xr.DataArray(dataframe,
                                              dims=['element', 'attribute'])

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

    def validate(self):
        """Make sure the number of vertices matches the associated data."""
        if self.data['edges'].shape[0] != self.data['attributes'].shape[0]:
            raise AttributeError('Attributes and edges must have the same length.')

    def to_xarray(self):
        a = xr.DataArray(self.vertex, dims=['points', 'XYZ'])
        b = xr.DataArray(self.edges, dims=['edges', 'node'])
        e = xr.DataArray(self.attributes, dims=['element', 'attribute'])
        c = xr.Dataset({'v': a, 'e': b, 'a': e})
        #x = c.reset_index('attribute')
        return c

    def to_disk(self, file: str, **kwargs):
        self.data.to_netcdf(file, **kwargs)
        return True


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
            data: Union[np.ndarray, xr.DataArray, xr.Dataset],
            data_name: str = 'data',
            coords: dict = None
    ):

        if type(data) == xr.Dataset:
            self.data = data

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



























