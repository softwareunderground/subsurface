from dataclasses import dataclass

from ..base_structures import UnstructuredData


@dataclass
class PointSet:
    """Class for pointset based data structures.

    This class uses UnstructuredData.vertex as cloud of points and the
    associated attributes. UnstructuredData.cells are not used.

    Args:
        data (UnstructuredData): Base object for unstructured data.

    """
    data: UnstructuredData
    
    def __init__(self, data: UnstructuredData):
        if data.cells.shape[1] > 1:
            raise AttributeError('data.cells must be of the format'
                                 'NDArray[(Any, 0), IntX] or NDArray[(Any, 1), IntX]')

        self.data = data

    @property
    def points(self) -> "np.ndarray":
        """Fetch the points/vertices dataframe."""
        return self.data.vertex

    @property
    def n_points(self):
        return self.data.vertex.shape[0]

    @property
    def point_data(self):
        """Fetch the scalar data associated with the vertices."""
        return self.data.attributes

    @property
    def point_data_dict(self):
        """Fetch the point data as a dictionary of numpy arrays."""
        return self.data.attributes_to_dict
