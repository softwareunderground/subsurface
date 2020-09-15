from dataclasses import dataclass

import numpy as np
import pandas as pd
import xarray as xr


@dataclass
class UnstructuredData:
    vertex: np.ndarray
    edges: np.ndarray
    attributes: pd.DataFrame = None

    def __post_init__(self):
        if self.attributes is None:
            self.attributes = pd.DataFrame(np.zeros((self.edges.shape[0], 0)))
        self.validate()

    @property
    def n_elements(self):
        return self.edges.shape[0]

    @property
    def n_points(self):
        return self.vertex.shape[0]

    @property
    def attributes_to_dict(self, **kwargs):
        return self.attributes_to_dict.to_dict(**kwargs)

    def validate(self):
        """Make sure the number of vertices matches the associated data."""
        if self.edges.shape[0] != self.attributes.shape[0]:
            raise AttributeError('Attributes and edges must have the same length.')


@dataclass
class StructuredData:
    structured_data: xr.Dataset
