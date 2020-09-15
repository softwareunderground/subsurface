"""These are classes that are point based and managed via Pandas DataFrames.

All data is tracked within internal DataFrames that we validate.

This is for holding general "mesh"-like data structures: point clouds,
linesets, triangulated surfaces, tetrahedralized volumes, octree grids, etc.

Regularly gridded dataset will NOT be managed by these classes but will use
``xarray`` under the hood.

"""

import numpy as np
import pandas as pd

from .base_structures import UnstructuredData
from .common import Common
from .errors import PyVistaImportError


class PointSet(Common):
    """Class for pointset based data structures.

    This class contains a data frame of vertices (points) and a data frame
    of data associated with each of those vertices.

    """

    def __init__(self,
                 data: UnstructuredData
                 ):
        """
        Initialize the pointset from a datafame.

        Parameters
        ----------
        points : pd.DataFrame
            A dataframe that has XYZ coordinates that are named as such.
            Additional columns will be tracked as point data.

        """
        if data.edges.shape[1] > 1:
            raise AttributeError('data.edges must be of the format'
                                 'NDArray[(Any, 0), IntX] or NDArray[(Any, 1), IntX]')

        self.data = data

    @property
    def points(self):
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
    def point_data_dict(self, **kwargs):
        """Fetch the point data as a dictionary of numpy arrays."""
        return self.data.attributes.to_dict(**kwargs)

    # def to_pyvista(self):
    #     """Create a PyVista PolyData mesh."""
    #     try:
    #         import pyvista as pv
    #     except:
    #         raise PyVistaImportError()
    #     point_cloud = pv.PolyData(self.points.values)
    #     point_cloud.point_arrays.update(self.point_data_dict)
    #     return point_cloud


class TriSurf(Common):
    """PointSet with triangle cells.

    This dataset defines cell connectivity between points to create
    triangulated surface.

    Contains an additional dataframe for the face connectivity.

    """

    def __init__(self,
                 data: UnstructuredData
                 ):
        """
        Initialize the pointset from a datafame.

        Parameters
        ----------
        points : pd.DataFrame
            A dataframe that has XYZ coordinates that are named as such.
            Additional columns will be tracked as point data.

        tri_indices : pd.DataFrame
            A three column dataframe of the the point indices for each triangle
            cell in the mesh. Each column corresponds to a triangle cell.

        """
        if data.edges.shape[1] != 3:
            raise AttributeError('data.edges must be of the format'
                                 'NDArray[(Any, 3), IntX]')

        self.data = data

    @property
    def triangles(self):
        return self.data.edges

    @property
    def n_triangles(self):
        return self.data.edges.shape[0]


class LineSet(Common):
    """PointSet with line cells.

    This dataset defines cell connectivity between points to create
    line segments.

    Contains an additional dataframe for the line connectivity.

    """

    def __init__(self,
                 data: UnstructuredData
                 ):
        """
        Initialize the pointset from a datafame.

        Parameters
        ----------
        points : pd.DataFrame
            A dataframe that has XYZ coordinates that are named as such.
            Additional columns will be tracked as point data.

        segment_indices : pd.DataFrame
            A two column dataframe of the indices of the end points for each
            line segment in the mesh. Each column corresponds to a line
            segment. If not specified, the vertices are connected in order,
            equivalent to ``segments=[[0, 1], [1, 2], [2, 3], ...]``.

        segment_data: pd.DataFrame
            A DataFrame of scalar data to associate with each line segment
            (cell).

        """
        if data.edges.shape[1] != 2:
            raise AttributeError('data.edges must be of the format'
                                 'NDArray[(Any, 3), IntX]')
        self.data = data

        # TODO: these must all be integer dtypes!

    def generate_default_edges(self):
        a = np.arange(0, self.data.n_elements - 1, dtype=np.int_)
        b = np.arange(1, self.data.n_elements, dtype=np.int_)
        self.data.edges = np.vstack([a, b])

    @property
    def segments(self):
        return self.data.edges

    @property
    def n_segments(self):
        return self.segments.shape[0]


class TetraMesh(Common):
    """PointSet with tetrahedron cells.

    This dataset defines cell connectivity between points to create
    tetrahedrons. This is volumetric.

    """

    def __init__(self,
                 data: UnstructuredData
                 ):
        """
        Initialize the pointset from a datafame.

        Parameters
        ----------
        points : pd.DataFrame
            A dataframe that has XYZ coordinates that are named as such.
            Additional columns will be tracked as point data.

        tetra_indices : pd.DataFrame
            A four column dataframe of the indices of the points for each
            tetrahedron in the mesh. Each column corresponds to a tetrahedron.
            Every tetrahedron is defined by the four points; where the first
            three (0,1,2) are the base of the tetrahedron which, using the
            right hand rule, forms a triangle whose normal points in the
            direction of the fourth point.

        tetra_data: pd.DataFrame
            A DataFrame of scalar data to associate with each line segment
            (cell).

        """
        if data.edges.shape[1] != 4:
            raise AttributeError('data.edges must be of the format'
                                 'NDArray[(Any, 4), IntX]')

        self.data = data

    @property
    def tetrahedrals(self):
        return self.data.edges

    @property
    def n_tetrahedrals(self):
        return self.tetrahedrals.shape[0]


