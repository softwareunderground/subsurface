from subsurface.writer.to_rex.common import write_data_block_header, encode
from subsurface.writer.to_rex.data_struct import RexMaterial


__all__ = ['material_encode', 'write_material_data']


def material_encode(rex_material: RexMaterial, data_id: int):
    # Write data block header for Material
    data_header_bytes = write_data_block_header(
        data_type=5,  # Material data type
        version_data=1,  # Version. Probably useful for operation counter
        size_data=68,  # Size of the block is FIXED
        data_id=data_id  # self.data_id
    )

    # Write Material
    material_bytes = write_material_data(rex_material)
    rex_bytes = data_header_bytes + material_bytes
    return rex_bytes


def write_material_data(rex_material: RexMaterial):
    """Writes a standard material definition block

    Returns: bytes (size:68) representation of the material

    """
    input_ = [(rex_material.ka_red, 'float32'),
              (rex_material.ka_green, 'float32'),
              (rex_material.ka_blue, 'float32'),
              (rex_material.ka_texture_ID, 'uint64'),
              (rex_material.ks_red, 'float32'),
              (rex_material.ks_green, 'float32'),
              (rex_material.ks_blue, 'float32'),
              (rex_material.ks_texture_ID, 'uint64'),
              (rex_material.kd_red, 'float32'),
              (rex_material.kd_green, 'float32'),
              (rex_material.kd_blue, 'float32'),
              (rex_material.kd_texture_ID, 'uint64'),
              (rex_material.ns, 'float32'),
              (rex_material.alpha, 'float32')]
    block_bytes = encode(input_)
    return block_bytes
