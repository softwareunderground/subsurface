from subsurface import UnstructuredData


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
