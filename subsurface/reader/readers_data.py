from dataclasses import dataclass, field
from typing import Union, Literal, Dict, Optional, List, Callable

import numpy as np
import pandas as pd
import xarray as xr
from pandas._typing import FilePathOrBuffer


@dataclass
class ReaderDataArgs:
    file_or_buffer: FilePathOrBuffer

    usecols: List[str] = None # Use a subset of columns
    col_names: List[Union[str, int]] = None # Give a name
    drop_cols: List[str] = None # Drop a subset of columns
    format: str = None
    index_map: Union[None, Callable, dict, pd.Series] = None
    columns_map: Union[None, Callable, dict, pd.Series] = None
    additional_reader_kwargs: dict = field(default_factory=dict)

    index_col: str = False
    header: Union[int, List[int]] = "infer"

    @property
    def pandas_reader_kwargs(self):
        attr_dict = {"names": self.col_names,
                     "header": self.header,
                     "index_col": self.index_col,
                     "usecols": self.usecols
                     }
        return {**attr_dict, **self.additional_reader_kwargs}

@dataclass
class ReaderDataUnstructured:
    reader_vertex_args: ReaderDataArgs
    reader_cells_args: ReaderDataArgs = None
    reader_vertex_attr_args: ReaderDataArgs = None
    reader_cells_attr_args: ReaderDataArgs = None


@dataclass
class RawDataOptions:
    swap_yz_cells: bool = False


@dataclass(init=False)
class RawDataUnstructured:
    vertex: np.ndarray
    cells: Union[np.ndarray, Literal["lines", "points"]]
    cells_attr: Union[None, pd.DataFrame, Dict[str, xr.DataArray]] = None
    vertex_attr: Union[None, pd.DataFrame, Dict[str, xr.DataArray]] = None

    def swap_yz_col_cells(self):
        cells_aux = self.cells.copy()
        self.cells[:, 1] = cells_aux[:, 2]
        self.cells[:, 2] = cells_aux[:, 1]
