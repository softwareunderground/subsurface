import pandas as pd
import xarray as xr
from typing import Union, Literal, Dict

import numpy as np
from dataclasses import dataclass


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
