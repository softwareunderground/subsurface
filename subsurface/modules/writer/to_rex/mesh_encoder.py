from subsurface.writer.to_rex.common import mesh_header_size, \
    write_data_block_header, encode
from subsurface.writer.to_rex.data_struct import RexMesh


__all__ = ['mesh_encode', 'write_mesh_coordinates', 'write_mesh_header']


def mesh_encode(rex_mesh: RexMesh, data_id: int):
    material_id = rex_mesh.material_id
    n_vtx_coord = rex_mesh.n_vtx
    n_triangles = rex_mesh.n_triangles
    n_vtx_colors = rex_mesh.n_color
    surface_name = rex_mesh.name
    ver_ravel = rex_mesh.ver_ravel
    tri_ravel = rex_mesh.tri_ravel
    c_r = rex_mesh.color_ravel

    # Write Mesh block - header
    mesh_header_bytes = write_mesh_header(
        n_vtx_coord / 3, n_triangles / 3,
        n_vtx_colors=n_vtx_colors / 3,
        start_vtx_coord=mesh_header_size,
        start_nor_coord=mesh_header_size + n_vtx_coord * 4,
        start_tex_coord=mesh_header_size + n_vtx_coord * 4,
        start_vtx_colors=mesh_header_size + n_vtx_coord * 4,
        start_triangles=mesh_header_size +
                        ((n_vtx_coord + n_vtx_colors) * 4),
        name=surface_name,
        material_id=material_id  # self.data_id + surface_df.shape[0]
    )

    # Write Mesh block - Vertex, triangles
    mesh_block_bytes = write_mesh_coordinates(ver_ravel,
                                              tri_ravel,
                                              colors=c_r  # When using
                                              # material we can avoid this
                                              )

    # Calculate the size of the mesh block
    mesh_block_size_no_data_block_header = len(mesh_header_bytes) + \
                                           len(mesh_block_bytes)  # This is cte 128

    # Write data block header for Mesh 1
    data_header_bytes = write_data_block_header(
        size_data=mesh_block_size_no_data_block_header,
        data_id=data_id,
        data_type=3,  # 3 for mesh
        version_data=1  # Probably useful for counting
        # the operation number
    )

    rex_bytes = data_header_bytes + mesh_header_bytes + mesh_block_bytes
    return rex_bytes


def write_mesh_coordinates(vertex, triangles, normal=None, texture=None,
                           colors=None):
    """Block with the coordinates of a mesh. This has to go with a header!

    Args:
        vertex (numpy.ndarray[float32]): Array of vertex XYZXYZ...
        triangles (numpy.ndarray[int32]): This is a list of integers which form
         one triangle. Please make sure that normal and texture coordinates are inline with the
         vertex coordinates. One index refers to the same normal and texture position. The
         triangle orientation is required to be counter-clockwise (CCW)
        normal (numpy.ndarray):
        texture (numpy.ndarray):
        colors (numpy.ndarray):

    Returns:

    """

    # ver = vertex.ravel()
    # tri = triangles.ravel()
    if normal is None:
        normal = []
    if texture is None:
        texture = []
    if colors is None:
        colors = []

    input_ = [(vertex, 'float32'),
              (normal, 'float32'),
              (texture, 'float32'),
              (colors, 'float32'),
              (triangles, 'uint32')]

    block_bytes = encode(input_)
    return block_bytes


def write_mesh_header(n_vtx_coord, n_triangles,
                      start_vtx_coord, start_nor_coord, start_tex_coord,
                      start_vtx_colors,
                      start_triangles,
                      name, material_id=1,  # material_id=9223372036854775807
                      n_nor_coord=0, n_tex_coord=0, n_vtx_colors=0,
                      lod=1, max_lod=1):
    """Function to write MESH DATA BLOCK header. The header size is fixed at 128 bytes.

    Args:
        n_vtx_coord: number of vertex coordinates
        n_triangles: number of triangles
        start_vtx_coord: start vertex coordinate block (relative to mesh block start)
        start_nor_coord: start vertex normals block (relative to mesh block start)
        start_tex_coord: start of texture coordinate block (relative to mesh block start)
        start_vtx_colors: start of colors block (relative to mesh block start)
        start_triangles: start triangle block for vertices (relative to mesh block start)
        name (str): Name of the mesh
        material_id (int):  id which refers to the corresponding material block in this file
        n_nor_coord:  number of normal coordinates (can be zero)
        n_tex_coord:  number of texture coordinates (can be zero)
        n_vtx_colors: number of vertex colors (can be zero)
        lod (int): level of detail for the given geometry
        max_lod (int): maximal level of detail for given geometry

    Returns:
        bytes: array of bytes
    """

    # Strings are immutable so there is no way to modify them in place
    str_size = len(name)  # Size of the actual name of the mesh
    rest_name = ' ' * (74 - str_size)  #
    full_name = name + rest_name

    input_ = [([lod, max_lod], 'uint16'),  # Level of detail
              ([n_vtx_coord,  # number of vertex coordinates
                n_nor_coord,  # number of normal coordinates (can be zero)
                n_tex_coord,  # number of texture coordinates (can be zero)
                n_vtx_colors,  # number of vertex colors (can be zero)
                n_triangles,  # number of triangles
                start_vtx_coord,
                # start vertex coordinate block (relative to mesh block start)
                start_nor_coord,
                # start vertex normals block (relative to mesh block start)
                start_tex_coord,
                # start of texture coordinate block (relative to mesh block start)
                start_vtx_colors,
                # start of colors block (relative to mesh block start)
                start_triangles
                # start triangle block for vertices (relative to mesh block start)
                ],
               'uint32'),
              (material_id, 'uint64'),
              # id which refers to the corresponding material block in this file
              (str_size, 'uint16'),  # size of the following string name
              (full_name, 'bytes')]  # name of the mesh (this is user-readable)

    block_bytes = encode(input_)
    return block_bytes
