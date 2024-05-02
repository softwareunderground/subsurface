from typing import Union, Dict, Literal, List

import numpy as np
import pandas as pd
import xarray as xr

from subsurface.core.structs.base_structures.base_structures_enum import SpecialCellCase


def vertex_and_cells_arrays_to_data_array(cells: Union[np.ndarray, Literal["lines", "points"], SpecialCellCase],
                                          vertex: np.ndarray):
    n_vertex = vertex.shape[0]
    if type(cells) is not np.ndarray:
        cells: np.ndarray = _create_default_cells_arg(
            cells=cells,
            n_vertex=n_vertex
        )
    n_cells = cells.shape[0]

    vertex_data_array = xr.DataArray(
        data=vertex,
        dims=['points', 'XYZ'],
        coords={'XYZ': ['X', 'Y', 'Z']}
    )
    cells_data_array = xr.DataArray(cells, dims=['cell', 'nodes'])
    return cells_data_array, n_cells, n_vertex, vertex_data_array


def raw_attributes_to_dict_data_arrays(
        default_attributes_name: str, n_items: int, dims: List[str],
        raw_attributes: Union[None, pd.DataFrame, Dict[str, xr.DataArray]]) \
        -> Dict[str, xr.DataArray]:
    if raw_attributes is None or type(raw_attributes) is pd.DataFrame:
        points_attributes_xarray_dict = {
                default_attributes_name: _data_array_attributes_from_raw_data(
                    raw_data=raw_attributes,
                    dims=dims,
                    n_rows=n_items
                )
        }
    else:
        points_attributes_xarray_dict = raw_attributes
    return points_attributes_xarray_dict


def _create_default_cells_arg(cells: Union[Literal["points", "lines"], SpecialCellCase],
                              n_vertex: int) -> np.ndarray:
    if cells is None or cells == 'points' or cells == SpecialCellCase.POINTS:
        cells_array = np.arange(0, n_vertex).reshape(-1, 1)
    elif cells == 'lines':
        a = np.arange(0, n_vertex - 1, dtype=np.int_)
        b = np.arange(1, n_vertex, dtype=np.int_)
        cells_array = np.vstack([a, b]).T
    elif type(cells) != np.ndarray:
        raise ValueError("cells must be either None (will default to 'points'),"
                         "'points', 'lines' or a 2D ndarray.")
    return cells_array


def _data_array_attributes_from_raw_data(raw_data: Union[None, pd.DataFrame],
                                         dims: List[str], n_rows: int) -> xr.DataArray:
    if raw_data is None:
        raw_data = pd.DataFrame(np.zeros((n_rows, 0)))

    if type(raw_data) is pd.DataFrame:
        data_array = xr.DataArray(raw_data, dims=dims)
    else:
        raise ValueError("cells_attributes must be either pd.DataFrame or " "None/default.")
    return data_array
