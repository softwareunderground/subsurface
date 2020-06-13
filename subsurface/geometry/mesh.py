"""These are classes that are point based and managed via Pandas DataFrames.

All data is tracked within internal DataFrames that we validate.

This is for holding general "mesh"-like data structures: point clouds,
linesets, triangulated surfaces, tetrahedralized volumes, octree grids, etc.

Regularly gridded dataset will NOT be managed by these classes but will use
``xarray`` under the hood.

"""

import numpy as np
import pandas as pd


from .common import Common
from .errors import PyVistaImportError


class PointSet(Common):
    """Base class for pointset based data structures.

    This class contains a data frame of vertices (points) and a data frame
    of data associated with each of those vertices.

    """

    def __init__(self,
                 data=None,
                 point_column_names=('x', 'y', 'z'),
                 ):
        """
        Initialize the pointset from a datafame.

        Parameters
        ----------
        data : pd.DataFrame
            A dataframe that has XYZ coordinates that are named as such.
            Additional columns will be tracked as point data.

        """
        self._df_points = pd.DataFrame(columns=['X', 'Y', 'Z'])
        self._df_point_data = pd.DataFrame()

        if isinstance(data, pd.DataFrame):
            if len(point_column_names) != 3:
                raise ValueError() # TODO: need much better checking than this
            self._df_points = data[point_column_names]
            data_column_names = data.keys().difference(point_column_names)
            self._df_point_data = data[data_column_names]

    @property
    def points(self):
        """Fetch the points/vertices dataframe."""
        return self._df_points

    @property
    def n_points(self):
        return len(self.points)

    @property
    def point_data(self):
        """Fetch the scalar data associated with the vertices."""
        return self._df_point_data

    @property
    def point_data_dict(self):
        """Fetch the point data as a disctionary of numpy arrays."""
        return dict(zip(self._df_point_data.index, self._df_point_data.values))

    def validate(self):
        """Make sure the number of vertices matches the associated data."""
        if len(self._df_points) != len(self._def_point_data):
            raise AssertionError()

    def to_pyvista(self):
        """Create a PyVista PolyData mesh."""
        try:
            import pyvista as pv
        except:
            raise PyVistaImportError()
        point_cloud = pv.PolyData(self.points.values)
        point_cloud.point_arrays.update(self.point_data_dict)
        return point_cloud


class _CellDataMixin(object):
    """A set of shared functionality for managing cell data.

    Cell data can live on faces, tetras, lines, etc. so rather than
    implementing cell data managers on each of those classes, mixin the
    functionality from this class.

    PointSets do not have cell data - opinionated choice by Bane.

    """
    def __init__(self, cell_data=None):
        self._df_cell_data = pd.DataFrame()
        if isinstance(cell_data, pd.DataFrame):
            self._df_cell_data = data

    @property
    def cell_data(self):
        """Fetch the scalar data associated with the cells.

        Cells can be triangles, lines, tets, etc.

        """
        return self._df_cell_data

    @property
    def cell_data_dict(self):
        """Fetch the cell data as a disctionary of numpy arrays."""
        return dict(zip(self._df_cell_data.index, self._df_cell_data.values))


class TriSurf(PointSet, _CellDataMixin):
    """PointSet with triangle cells.

    This dataset defines cell connectivity between points to create
    triangulated surface.

    Contains an additional dataframe for the face connectivity.

    """
    def __init__(self,
                 data=None,
                 tri_indices=None,
                 tri_data=None,
                 point_column_names=('x', 'y', 'z'),
                 ):
        """
        Initialize the pointset from a datafame.

        Parameters
        ----------
        data : pd.DataFrame
            A dataframe that has XYZ coordinates that are named as such.
            Additional columns will be tracked as point data.

        tri_indices : pd.DataFrame
            A three column dataframe of the the point indices for each triangle
            cell in the mesh. Each column corresponds to a triangle cell.

        """
        PointSet.__init__(self, data=data, point_column_names=point_column_names)
        _CellDataMixin.__init__(self, cell_data=tri_data)

        # TODO: these must all be integer dtypes!
        self._df_tri_indices = pd.DataFrame(columns=['a', 'b', 'c'])

    @property
    def triangles(self):
        return self._df_tri_indices

    @property
    def n_triangles(self):
        return len(self.triangles)

    def to_pyvista(self):
        try:
            import pyvista as pv
        except:
            raise PyVistaImportError()
        vertices = self.points.values
        faces = self.triangles.values
        faces = np.c_[np.full(len(faces), 3), faces]
        mesh = pv.PolyData(vertices, faces)
        mesh.point_arrays.update(self.point_data_dict)
        mesh.cell_arrays.update(self.cell_data_dict)
        return mesh


class LineSet(PointSet, _CellDataMixin):
    """PointSet with line cells.

    This dataset defines cell connectivity between points to create
    line segments.

    Contains an additional dataframe for the line connectivity.

    """
    def __init__(self,
                 data=None,
                 segment_indices=None,
                 segment_data=None,
                 point_column_names=('x', 'y', 'z'),
                 ):
        """
        Initialize the pointset from a datafame.

        Parameters
        ----------
        data : pd.DataFrame
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
        PointSet.__init__(self, data=data, point_column_names=point_column_names)
        _CellDataMixin.__init__(self, cell_data=segment_data)

        # TODO: these must all be integer dtypes!
        self._df_segment_indices = pd.DataFrame(columns=['a', 'b'])

    @property
    def segments(self):
        return self._df_segment_indices

    @property
    def n_segments(self):
        return len(self.segments)

    def to_pyvista(self):
        try:
            import pyvista as pv
        except:
            raise PyVistaImportError()
        vertices = self.points.values
        lines = self.segments.values
        lines = np.c_[np.full(len(lines), 2), lines]
        lineset = pv.PolyData()
        lineset.points = vertices
        lineset.line = lines
        lineset.point_arrays.update(self.point_data_dict)
        lineset.cell_arrays.update(self.cell_data_dict)
        return lineset
