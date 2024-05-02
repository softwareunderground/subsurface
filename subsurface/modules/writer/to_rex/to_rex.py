from typing import List

from subsurface.writer.to_rex.common import file_header_size, encode
from subsurface.writer.to_rex.data_struct import RexLineSet, RexMesh, RexMaterial
from subsurface.writer.to_rex.material_encoder import material_encode
from subsurface.writer.to_rex.mesh_encoder import mesh_encode


__all__ = ['numpy_to_rex', 'w_data_blocks', 'w_block_data_type',
           'w_file_header_and_coord_system_block',
           'w_file_header_and_coord_system_block', 'write_rex_file',
           'read_rex_file']


def numpy_to_rex(
        rex_line_set: List[RexLineSet] = None,
        rex_meshes: List[RexMesh] = None,
        rex_material: List[RexMaterial] = None
):
    if rex_line_set is None:
        rex_line_set = list()
    if rex_meshes is None:
        rex_meshes = list()
    if rex_material is None:
        rex_material = list()

    data_block_bytes = bytearray()
    byte_size = 0

    data_block_bytes, data_id = w_data_blocks(rex_meshes, rex_material)

    n_data_blocks = data_id
    header_and_coord_block_bytes = w_file_header_and_coord_system_block(
        n_data_blocks=n_data_blocks,
        size_data_blocks=len(data_block_bytes),
        start_data=file_header_size
    )

    return header_and_coord_block_bytes + data_block_bytes


def w_data_blocks(rex_meshes: List[RexMesh], rex_material: List[RexMaterial]):
    data_id = 0

    rmesh_bytes, data_id = w_block_data_type(mesh_encode, rex_meshes, data_id)
    rmaterial_bytes, data_id = w_block_data_type(material_encode, rex_material,
                                                 data_id)

    blocks_bytes = rmesh_bytes + rmaterial_bytes
    return blocks_bytes, data_id


def w_block_data_type(encoder, rex_objects: List, data_id: int):
    data_block_bytes = bytearray()
    for rex_obj in rex_objects:
        data_block_bytes += encoder(rex_obj, data_id=data_id)
        data_id += 1

    return data_block_bytes, data_id


def w_file_header_and_coord_system_block():
    return


def w_file_header_and_coord_system_block(n_data_blocks, size_data_blocks, version=1,
                                         start_data=86, srid=3876, offsets=None):
    """
    Function that writes the header block of a rexfile:

    Args:
        n_data_blocks:
        size_data_blocks:
        version (int): Version of the file
        start_data (int): Position where data start. This is after the header
         and coordinate system. If everything works fine it should be 86
        srid (int): Spatial reference system identifier (srid)
        offsets:

    Returns:

    """
    reserved = '0' * 42
    if offsets is None:
        offsets = [0, 0, 0]

    input_ = [('REX1', 'bytes'),  # REX1
              (version, 'uint16'),  # file version
              (0, 'uint32'),  # CRC32
              (n_data_blocks, 'uint16'),  # Number of DATA BLOCKS
              (start_data, 'uint16'),  # StartData
              (size_data_blocks, 'uint64'),  # Size of all data blocks
              (reserved, 'bytes'),  # Reserved
              # Coordinate system block
              (srid, 'uint32'),  # Spatial reference system identifier (srid)
              (4, 'uint16'),  # Size of the name of the used system.
              ('EPSG', 'bytes'),  # name of the used system.
              (offsets, 'float32')]  # Global x, y, z offset

    block_bytes = encode(input_)
    return block_bytes


def write_rex_file(bytes, path: str):
    """Write to disk a rexfile from its binary format"""

    new_file = open(path + ".rex", "wb")
    new_file.write(bytes)
    return True


def read_rex_file(path: str) -> bytes:
    with open(path, "rb") as f:
        bytes_read = f.read()
    return bytes_read
