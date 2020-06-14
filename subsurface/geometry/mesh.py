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
                 points=None,
                 point_column_names=('x', 'y', 'z'),
                 ):
        """
        Initialize the pointset from a datafame.

        Parameters
        ----------
        points : pd.DataFrame
            A dataframe that has XYZ coordinates that are named as such.
            Additional columns will be tracked as point data.

        """
        self._df_points = pd.DataFrame(columns=['X', 'Y', 'Z'])
        self._df_point_data = pd.DataFrame()

        if isinstance(points, pd.DataFrame):
            if len(point_column_names) != 3:
                raise ValueError() # TODO: need much better checking than this
            self._df_points = points[list(point_column_names)]
            data_column_names = points.keys().difference(point_column_names)
            self._df_point_data = points[data_column_names]

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
        return dict(zip(self._df_point_data.keys(), self._df_point_data.values.T))

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
            self._df_cell_data = cell_data

    @property
    def cell_data(self):
        """Fetch the scalar data associated with the cells.

        Cells can be triangles, lines, tets, etc.

        """
        return self._df_cell_data

    @property
    def cell_data_dict(self):
        """Fetch the cell data as a disctionary of numpy arrays."""
        return dict(zip(self._df_cell_data.keys(), self._df_cell_data.values.T))

    @property
    def n_cells(self):
        return len(self.cell_data)


class TriSurf(PointSet, _CellDataMixin):
    """PointSet with triangle cells.

    This dataset defines cell connectivity between points to create
    triangulated surface.

    Contains an additional dataframe for the face connectivity.

    """
    def __init__(self,
                 points=None,
                 tri_indices=None,
                 tri_data=None,
                 point_column_names=('x', 'y', 'z'),
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
        PointSet.__init__(self, points=points, point_column_names=point_column_names)
        _CellDataMixin.__init__(self, cell_data=tri_data)

        # TODO: these must all be integer dtypes!
        self._df_tri_indices = pd.DataFrame(columns=['a', 'b', 'c'])
        if isinstance(tri_indices, pd.DataFrame):
            # TODO: run checks to valides indices, dtype, etc.
            self._df_tri_indices = tri_indices

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
                 points=None,
                 segment_indices=None,
                 segment_data=None,
                 point_column_names=('x', 'y', 'z'),
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
        PointSet.__init__(self, points=points, point_column_names=point_column_names)
        _CellDataMixin.__init__(self, cell_data=segment_data)

        # TODO: these must all be integer dtypes!
        self._df_segment_indices = pd.DataFrame(columns=['a', 'b'])
        if segment_indices is None:
            # Automattically generate segment indices in order
            a = np.arange(0, self.n_points-1, dtype=np.int_)
            b = np.arange(1, self.n_points, dtype=np.int_)
            self._df_segment_indices['a'] = a
            self._df_segment_indices['b'] = b
        elif isinstance(segment_indices, pd.DataFrame):
            # TODO: run checks!!
            self._df_segment_indices = segment_indices

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



class TetraMesh(PointSet, _CellDataMixin):
    """PointSet with tetrahedron cells.

    This dataset defines cell connectivity between points to create
    tetrahedrons. This is volumetric.

    """
    def __init__(self,
                 points=None,
                 tetra_indices=None,
                 tetra_data=None,
                 point_column_names=('x', 'y', 'z'),
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
        PointSet.__init__(self, points=points, point_column_names=point_column_names)
        _CellDataMixin.__init__(self, cell_data=tetra_data)

        # TODO: these must all be integer dtypes!
        self._df_tetra_indices = pd.DataFrame(columns=['a', 'b', 'c', 'd'])
        if isinstance(tetra_indices, pd.DataFrame):
            # TODO: run checks!!
            self._df_tetra_indices = tetra_indices

    @property
    def tetrahedrals(self):
        return self._df_tetra_indices

    @property
    def n_tetrahedrals(self):
        return len(self.tetrahedrals)

    def to_pyvista(self):
        try:
            import pyvista as pv
            import vtk
        except:
            raise PyVistaImportError()
        vertices = self.points.values
        tets = self.tetrahedrals.values
        cells = np.c_[np.full(len(tets), 4), tets]
        ctypes = np.array([vtk.VTK_TETRA,], np.int32)
        mesh = pv.UnstructuredGrid(cells, ctypes, vertices)
        mesh.point_arrays.update(self.point_data_dict)
        mesh.cell_arrays.update(self.cell_data_dict)
        return mesh


class CurvilinearMesh(PointSet, _CellDataMixin):
    """Container for curvilinear mesh grids.

    This is analogous to PyVista's StructuredGrid class or discretize's
    CurviMesh class.

    """
    def __init__(self,
                 points,
                 dimensions,
                 cell_data=None,
                 point_column_names=('x', 'y', 'z'),
                 ):
        """
        Initialize the mesh from datafames.

        TODO: dimensions is not tracked in the dataframe... perhaps we need
        an adapter to do this?

        Parameters
        ----------
        points : pd.DataFrame
            A dataframe that has XYZ coordinates that are named as such.
            Additional columns will be tracked as point data.

        dimensions : tuple(int)
            A length 3 Tuple of integers for the dimensions of the structured
            grid. The product of this tuple should equal the number of points.
            When reshaping the points array to this shape + 3, a typical
            meshgrid is created.

        cell_data: pd.DataFrame
            A DataFrame of scalar data to associate with each hexahedron
            (cell).

        """
        PointSet.__init__(self, points=points, point_column_names=point_column_names)
        _CellDataMixin.__init__(self, cell_data=cell_data)

        self.dimensions = dimensions # Uses property setter

    def _validate_dimensions(self, dimensions):
        if np.product(dimensions) != self.n_points:
            raise ValueError('dimensions do not match points')

    @property
    def dimensions(self):
        return self._dimensions

    @dimensions.setter
    def dimensions(self, dimensions):
        self._validate_dimensions(dimensions)
        self._dimensions = dimensions

    @property
    def meshgrid(self):
        return np.moveaxis(self.points.values.reshape((*self.dimensions, 3)), -1, 0)

    def to_pyvista(self):
        try:
            import pyvista as pv
            import vtk
        except:
            raise PyVistaImportError()
        mesh = pv.StructuredGrid(*self.meshgrid)
        mesh.point_arrays.update(self.point_data_dict)
        mesh.cell_arrays.update(self.cell_data_dict)
        return mesh


class OctreeMesh(PointSet, _CellDataMixin):
    """TODO: implement as Dom discussed with data frames to track the levels.
    """
    pass
