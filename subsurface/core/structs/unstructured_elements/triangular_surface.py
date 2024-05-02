from ..base_structures import UnstructuredData, StructuredData


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
    def has_texture_data(self):
        return self.texture is not None and self.texture_origin is not None and self.texture_point_u is not None and self.texture_point_v is not None
    
    @property
    def triangles(self):
        return self.mesh.cells

    @property
    def n_triangles(self):
        return self.mesh.cells.shape[0]
