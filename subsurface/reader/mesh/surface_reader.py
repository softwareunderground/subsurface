from typing import Union, Callable

import pandas as pd

from subsurface.reader.readers_data import ReaderFilesHelper
from subsurface.utils.utils_core import get_extension
import numpy as np


__all__ = ['read_mesh_file_to_vertex', 'read_mesh_file_to_cells',
           'read_mesh_file_to_attr', 'mesh_csv_to_vertex', 'mesh_csv_to_cells',
           'mesh_csv_to_attributes', 'get_cells_from_df',
           'cells_from_delaunay', 'get_vertices_from_df', 'map_columns_names',
           'dxf_to_vertex_edges', 'dxf_to_vertex']


def read_mesh_file_to_vertex(reader_args: ReaderFilesHelper) -> np.ndarray:
    if reader_args.format == '.csv':
        vertex = mesh_csv_to_vertex(reader_args.file_or_buffer, reader_args.columns_map,
                                    **reader_args.pandas_reader_kwargs)
    elif reader_args.format == '.dxf':
        vertex = dxf_to_vertex(reader_args.file_or_buffer)
    else:
        raise ValueError(f"Subsurface is not able to read the following extension: {reader_args.format}")
    return vertex


def read_mesh_file_to_cells(reader_args: ReaderFilesHelper) -> np.ndarray:
    extension = reader_args.format

    if extension == '.csv':
        cells = mesh_csv_to_cells(reader_args.file_or_buffer, reader_args.columns_map,
                                  **reader_args.pandas_reader_kwargs)
    else:
        raise ValueError(f"Subsurface is not able to read the following extension: {extension}")
    return cells


def read_mesh_file_to_attr(reader_args: ReaderFilesHelper):
    extension = reader_args.format
    if extension == ".csv":
        attr = mesh_csv_to_attributes(reader_args.file_or_buffer,
                                      reader_args.columns_map,
                                      **reader_args.pandas_reader_kwargs)
    else:
        raise ValueError(f"Subsurface is not able to read the following extension: {extension}")
    return attr


def mesh_csv_to_vertex(path_to_file: str, columns_map: Union[None, Callable, dict, pd.Series] = None,
                       **reader_kwargs) -> np.ndarray:
    data = pd.read_csv(path_to_file, **reader_kwargs)
    if columns_map is not None: map_columns_names(columns_map, data)
    return get_vertices_from_df(data)


def mesh_csv_to_cells(path_to_file: str, columns_map: Union[None, Callable, dict, pd.Series] = None,
                      **reader_kwargs) -> np.ndarray:
    data = pd.read_csv(path_to_file, **reader_kwargs)
    if columns_map is not None: map_columns_names(columns_map, data)
    return get_cells_from_df(data)


def mesh_csv_to_attributes(path_to_file: str,
                           columns_map: Union[None, Callable, dict, pd.Series] = None,
                           **reader_kwargs) -> pd.DataFrame:

    data = pd.read_csv(path_to_file, **reader_kwargs)
    if columns_map is not None:
        map_columns_names(columns_map, data)
    return data


def get_cells_from_df(data):
    try:
        cells = data[['e1', 'e2', 'e3']].dropna().astype('int').values
    except KeyError:
        raise KeyError('Columns e1, e2, and e3 must be present in the data set. Use'
                       'columns_map to map other names')
    return cells


def cells_from_delaunay(vertex):
    import pyvista as pv
    a = pv.PolyData(vertex)
    b = a.delaunay_2d().faces
    cells = b.reshape(-1, 4)[:, 1:]
    return cells


def get_vertices_from_df(data):
    try:
        vertex = data[['x', 'y', 'z']].values
    except KeyError:
        raise KeyError('Columns x, y, and z must be present in the data set. Use'
                       'columns_map to map other names')
    return vertex


def map_columns_names(columns_map: Union[Callable, dict, pd.Series], data: pd.DataFrame):
    data.columns = data.columns.map(columns_map)
    if data.columns.isin(['x', 'y', 'z']).any() is False:
        raise AttributeError('At least x, y, z must be passed to `columns_map`')

    return data.columns


def dxf_to_vertex_edges(file_or_buffer):
    from scipy.spatial.qhull import Delaunay
    vertex = dxf_to_vertex(file_or_buffer)
    tri = Delaunay(vertex[:, [0, 1]])
    faces = tri.simplices
    return faces, vertex


def dxf_to_vertex(file_or_buffer):
    import ezdxf
    dataset = ezdxf.readfile(file_or_buffer)
    vertex = []
    entity = dataset.modelspace()
    for e in entity:
        vertex.append(e[0])
        vertex.append(e[1])
        vertex.append(e[2])
    vertex = np.array(vertex)
    vertex = np.unique(vertex, axis=0)
    return vertex
