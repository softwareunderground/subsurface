"""These are classes that are point based and managed via Pandas DataFrames.

All data is tracked within internal DataFrames that we validate.

This is for holding general "mesh"-like data structures: point clouds,
linesets, triangulated surfaces, tetrahedralized volumes, octree grids, etc.

Regularly gridded dataset will NOT be managed by these classes but will use
``xarray`` under the hood.

"""

import numpy as np
from .base_structures import UnstructuredData, StructuredData


__all__ = ['PointSet', 'TriSurf', 'LineSet', 'TetraMesh']


class PointSet:
    """Class for pointset based data structures.

    This class uses UnstructuredData.vertex as cloud of points and the
    associated attributes. UnstructuredData.cells are not used.

    Args:
        data (UnstructuredData): Base object for unstructured data.

    """

    def __init__(self, data: UnstructuredData):
        if data.cells.shape[1] > 1:
            raise AttributeError('data.cells must be of the format'
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
    def point_data_dict(self):
        """Fetch the point data as a dictionary of numpy arrays."""
        return self.data.attributes_to_dict


class TriSurf:
    """PointSet with triangle cells.

    This dataset defines cell/element connectivity between points to create
    triangulated surface.

    Uses UnstructuredData.cells for the face connectivity.

    Args:
        mesh (UnstructuredData): Base object for unstructured data.
         data.cells  represent the point indices for each triangle
         in the mesh. Each column corresponds to a triangle edge.
        texture (StructuredData): 2D StructuredData with data to be mapped
         on the mesh

    Keyword Args:
        texture_origin : tuple(float)
            Length 3 iterable of floats defining the XYZ coordinates of the
            BOTTOM LEFT CORNER of the plane

        texture_point_u : tuple(float)
            Length 3 iterable of floats defining the XYZ coordinates of the
            BOTTOM RIGHT CORNER of the plane

        texture_point_v : tuple(float)
            Length 3 iterable of floats defining the XYZ coordinates of the
            TOP LEFT CORNER of the plane
    """

    def __init__(self,
                 mesh: UnstructuredData,
                 texture: StructuredData = None,
                 **kwargs
                 ):
        if mesh.cells.shape[1] != 3:
            raise AttributeError('data.cells must be of the format'
                                 'NDArray[(Any, 3), IntX]')

        self.mesh: UnstructuredData = mesh
        self.texture: StructuredData = texture
        self.texture_origin = kwargs.get('texture_origin', None)
        self.texture_point_u = kwargs.get('texture_point_u', None)
        self.texture_point_v = kwargs.get('texture_point_v', None)

    @property
    def triangles(self):
        return self.mesh.cells

    @property
    def n_triangles(self):
        return self.mesh.cells.shape[0]


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


class TetraMesh:
    """PointSet with tetrahedron cells.

    This dataset defines cell connectivity between points to create
    tetrahedrons. This is volumetric.

    Args:

        data (UnstructuredData): Base object for unstructured data.

         data.cells represent the indices of the points for each
         tetrahedron in the mesh. Each column corresponds to a tetrahedron.
         Every tetrahedron is defined by the four points; where the first
         three (0,1,2) are the base of the tetrahedron which, using the
         right hand rule, forms a triangle whose normal points in the
         direction of the fourth point.

    """

    def __init__(self, data: UnstructuredData):
        if data.cells.shape[1] != 4:
            raise AttributeError('data.cells must be of the format'
                                 'NDArray[(Any, 4), IntX]')
        self.data = data

    @property
    def tetrahedrals(self):
        return self.data.cells

    @property
    def n_tetrahedrals(self):
        return self.tetrahedrals.shape[0]
