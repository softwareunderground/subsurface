import numpy as np
import pandas as pd

from ..base_structures import UnstructuredData


class LineSet:
    """PointSet with line cells.

    This dataset defines cell connectivity between points to create
    line segments.

    Args:
        data (UnstructuredData): Base object for unstructured data.

         data.cells represent the indices of the end points for each
         line segment in the mesh. Each column corresponds to a line
         segment. If not specified, the vertices are connected in order,
         equivalent to ``segments=[[0, 1], [1, 2], [2, 3], ...]``

        radius (float): Thickness of the line set
    """

    def __init__(self, data: UnstructuredData, radius: float = 1):

        self.data: UnstructuredData = data
        self.radius = radius

        if data.cells is None or data.cells.shape[1] < 2:
            self.generate_default_cells()

        elif data.cells.shape[1] != 2:
            raise AttributeError('data.cells must be of the format'
                                 'NDArray[(Any, 2), IntX]')

        # TODO: these must all be integer dtypes!

    def get_first_index_per_well(self, attr_hole_id: str):
        """ Method to get the first index of each well in the LineSet

        Returns:
            np.ndarray[(Any,), IntX]

        """
        import xarray as xr
        dataset: xr.Dataset = self.data.data
        dataframe: pd.DataFrame = self.data.attributes
        array = dataframe[attr_hole_id].values
        
        first_index = np.where(array[:-1] != array[1:])[0]
        return first_index
        
    
    def generate_default_cells(self):
        """ Method to generate cells based on the order of the vertex. This
        only works if the LineSet only represents one single line

        Returns:
            np.ndarray[(Any, 2), IntX]

        """
        a = np.arange(0, self.data.n_points - 1, dtype=np.int_)
        b = np.arange(1, self.data.n_points, dtype=np.int_)
        return np.vstack([a, b]).T

    @property
    def segments(self):
        return self.data.cells

    @property
    def n_segments(self):
        return self.segments.shape[0]
