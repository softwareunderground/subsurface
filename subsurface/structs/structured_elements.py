"""For regularly gridded datasets like rasters and tensor meshes.

"""

import xarray as xr

from .common import Common
from .base_structures import StructuredData


class OctreeMesh(Common):
    """
    TODO: implement as Dom discussed with data frames to track the levels.
    """
    def __init__(self, data: StructuredData):
        raise NotImplementedError


class StructuredSurface(Common):
    def __init__(self, structured_data: StructuredData):
        # TODO check structured_data has two coordinates
        self.ds = structured_data

    # Add pyvista methods of gridded data


class StructuredGrid(Common):
    # TODO check structured_data has three coordinates
    def __init__(self, structured_data: StructuredData):
        self.ds = structured_data
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

        self.dimensions = dimensions  # Uses property setter

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
