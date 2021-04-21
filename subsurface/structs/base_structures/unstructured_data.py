from dataclasses import dataclass
from typing import Union, Dict, Mapping, Hashable, Any, Literal, List

import numpy as np
import pandas as pd
import xarray as xr

from subsurface.reader.readers_data import RawDataUnstructured


__all__ = ['UnstructuredData', ]


@dataclass(frozen=True)
class UnstructuredData:
    data: xr.Dataset
    cells_attr_name: str = "cell_attrs"
    vertex_attr_name: str = "vertex_attrs"

    """Primary structure definition for unstructured data

    Attributes:
        data (`xarray.Dataset`): Data structure where we store

    Args:

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

    def __post_init__(self):
        self._validate()

    def __repr__(self):
        return self.data.__repr__()

    @classmethod
    def from_raw_data(cls, raw_data: RawDataUnstructured,
                      coords: Mapping[Hashable, Any] = None,
                      xarray_attributes: Mapping[Hashable, Any] = None,
                      default_cells_attributes_name: str = "cell_attrs",
                      default_points_attributes_name: str = "vertex_attrs"
                      ):
        return cls.from_array(raw_data.vertex, raw_data.cells, raw_data.cells_attr, raw_data.vertex_attr, coords,
                              xarray_attributes, default_cells_attributes_name, default_points_attributes_name)

    @classmethod
    def from_array(
            cls,
            vertex: np.ndarray,
            cells: Union[np.ndarray, Literal["lines", "points"]],
            cells_attr: Union[None, pd.DataFrame, Dict[str, xr.DataArray]] = None,
            vertex_attr: Union[None, pd.DataFrame, Dict[str, xr.DataArray]] = None,
            coords: Mapping[Hashable, Any] = None,
            xarray_attributes: Mapping[Hashable, Any] = None,
            default_cells_attr_name: str = "cell_attrs",
            default_points_attr_name: str = "vertex_attrs",
            attributes: Union[None, pd.DataFrame, Dict[str, xr.DataArray]] = None  # TODO Obsolete
    ):
        """ Constructor of UnstructuredData from arrays or pandas DataFrames.

        Args:
            vertex (np.ndarray): NDArray[(Any, 3), FloatX]: XYZ point data
            cells (Union[np.ndarray, Literal["lines", "points"]]): NDArray[(Any, ...), IntX]:
             Combination of vertex that create different geometric elements. If
             str use default values for either points or lines
            cells_attr (Union[None, pd.DataFrame, Dict[str, xr.DataArray]]]: Number associated to an element
            vertex_attr (Union[None, pd.DataFrame, Dict[str, xr.DataArray]]]: Number
             associated to points
            coords:
            xarray_attributes:
            attributes:
            default_cells_attr_name:
            default_points_attr_name:

        Returns:

        """
        if attributes is not None:
            cells_attr = attributes

        cells_data_array, n_cells, n_vertex, vertex_data_array = cls.vertex_and_cells_arrays_to_data_array(cells,
                                                                                                           vertex)
        points_attributes_xarray_dict = cls.raw_attributes_to_dict_data_arrays(
            default_points_attr_name, n_vertex, ["points", "vertex_attr"], vertex_attr)
        cells_attributes_xarray_dict = cls.raw_attributes_to_dict_data_arrays(
            default_cells_attr_name, n_cells, ["cell", "cell_attr"], cells_attr)

        xarray_dict = {
            "vertex": vertex_data_array, "cells": cells_data_array,
            **cells_attributes_xarray_dict,
            **points_attributes_xarray_dict
        }

        default_cells_attr_name = cells_attributes_xarray_dict.get(None, next(iter(cells_attributes_xarray_dict)))
        default_points_attr_name = points_attributes_xarray_dict.get(None,
                                                                     next(iter(points_attributes_xarray_dict)))

        return cls.from_data_arrays_dict(xarray_dict, coords, xarray_attributes,
                                         default_cells_attr_name, default_points_attr_name)

    @classmethod
    def from_data_arrays_dict(cls, xarray_dict: Dict[str, xr.DataArray],
                              coords: Mapping[Hashable, Any] = None,
                              xarray_attributes: Mapping[Hashable, Any] = None,
                              default_cells_attributes_name="cell_attrs",
                              default_points_attributes_name="vertex_attrs"):

        ds = xr.Dataset(xarray_dict, coords=coords, attrs=xarray_attributes)

        # Try to unstack pandas dataframe if exist
        # TODO: This is an issue in wells. If it is only there maybe we should move it there
        try:
            ds = ds.reset_index('cell')
        except KeyError:
            pass

        return cls(ds, default_cells_attributes_name, default_points_attributes_name)

    @classmethod
    def raw_attributes_to_dict_data_arrays(
            cls, default_attributes_name: str, n_items: int, dims: List[str],
            raw_attributes: Union[None, pd.DataFrame, Dict[str, xr.DataArray]]) \
            -> Dict[str, xr.DataArray]:

        if raw_attributes is None or type(raw_attributes) == pd.DataFrame:
            points_attributes_xarray_dict = {
                default_attributes_name: cls.data_array_attributes_from_raw_data(raw_attributes, dims, n_items)
            }
        else:
            points_attributes_xarray_dict = raw_attributes
        return points_attributes_xarray_dict

    @classmethod
    def vertex_and_cells_arrays_to_data_array(cls, cells: Union[np.ndarray, Literal["lines", "points"]],
                                              vertex: np.ndarray):
        n_vertex = vertex.shape[0]
        if type(cells) != np.ndarray:
            cells = cls.create_default_cells_arg(cells, n_vertex)
        n_cells = cells.shape[0]
        vertex_data_array = xr.DataArray(vertex, dims=['points', 'XYZ'],
                                         coords={'XYZ': ['X', 'Y', 'Z']})
        cells_data_array = xr.DataArray(cells, dims=['cell', 'nodes'])
        return cells_data_array, n_cells, n_vertex, vertex_data_array

    @classmethod
    def data_array_attributes_from_raw_data(cls, raw_data: Union[None, pd.DataFrame],
                                            dims: List[str], n_rows: int) -> xr.DataArray:
        if raw_data is None:
            raw_data = pd.DataFrame(np.zeros((n_rows, 0)))

        if type(raw_data) is pd.DataFrame:
            data_array = xr.DataArray(raw_data, dims=dims)
        else:
            raise ValueError("cells_attributes must be either pd.DataFrame or "
                             "None/default.")
        return data_array

    @classmethod
    def create_default_cells_arg(cls, cells: Literal["points", "lines"], n_vertex: int) -> np.ndarray:

        if cells is None or cells == 'points':
            cells = np.arange(0, n_vertex).reshape(-1, 1)
        elif cells == 'lines':
            a = np.arange(0, n_vertex - 1, dtype=np.int_)
            b = np.arange(1, n_vertex, dtype=np.int_)
            cells = np.vstack([a, b]).T
        elif type(cells) != np.ndarray:
            raise ValueError("cells must be either None (will default to 'points'),"
                             "'points', 'lines' or a 2D ndarray.")
        return cells

    def _validate(self):
        try:
            _ = self.data[self.cells_attr_name]['cell']
            _ = self.data[self.cells_attr_name]['cell_attr']

        except KeyError:
            raise KeyError('Cell attribute DataArrays must contain dimension cell and '
                           'cell_attr')

        try:
            _ = self.data[self.vertex_attr_name]['vertex_attr']
            _ = self.data[self.vertex_attr_name]['points']
        except KeyError:
            raise KeyError('Point attribute DataArrays must contain dimensions'
                           ' points and vertex_attr.')

        # Make sure the number of vertices matches the associated data.
        if self.data['cells']['cell'].size != self.data[self.cells_attr_name]['cell'].size:
            raise AttributeError('Attributes and cells must have the same length.')

        if self.n_points != self.data[self.vertex_attr_name]['points'].size:
            raise AttributeError('points_attributes and vertex must have the same length.')

    @property
    def vertex(self):
        return self.data['vertex'].values

    @property
    def cells(self):
        return self.data['cells'].values

    @property
    def attributes(self):
        xarray = self.data[self.cells_attr_name]
        return xarray.to_dataframe()[self.cells_attr_name].unstack(level=1)

    @attributes.setter
    def attributes(self, dataframe):
        self.data[self.cells_attr_name] = xr.DataArray(dataframe, dims=['element', 'cell_attr'])

    @property
    def points_attributes(self):
        return self.data[self.vertex_attr_name].to_dataframe()[
            self.vertex_attr_name].unstack(level=1)

    @points_attributes.setter
    def points_attributes(self, dataframe):
        self.data[self.vertex_attr_name] = xr.DataArray(dataframe, dims=['points', 'vertex_attr'])

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
        return self.points_attributes.to_dict(orient)

    def to_xarray(self):
        a = xr.DataArray(self.vertex, dims=['points', 'XYZ'])
        b = xr.DataArray(self.cells, dims=['cells', 'node'])
        e = xr.DataArray(self.attributes, dims=['element', 'cell_attr'])
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
        vertex_attribute = self.points_attributes.values.astype('float32').tobytes(order)
        bytearray_le = vertex + cells + cell_attribute + vertex_attribute
        return bytearray_le
