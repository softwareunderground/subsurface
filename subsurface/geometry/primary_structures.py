from dataclasses import dataclass

import numpy as np
import pandas as pd
import xarray as xr


@dataclass
class UnstructuredData:
    vertex: np.ndarray
    edges: np.ndarray
    attributes: pd.DataFrame

    @property
    def n_points(self):
        return len(self.vertex)


@dataclass
class StructuredData:
    structured_data: xr.Dataset
