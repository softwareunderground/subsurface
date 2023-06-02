from typing import Union, Callable

import numpy as np
import pandas as pd


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
