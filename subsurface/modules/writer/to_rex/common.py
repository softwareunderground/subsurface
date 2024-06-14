import numpy as np

__all__ = ['write_data_block_header', 'encode']

rexFileHeaderSize = 64
rexCoordSize = 22

file_header_size = 86
rexDataBlockHeaderSize = 16

file_header_and_data_header = 102
mesh_header_size = 128
all_header_size = 230

# Supported block types
# typeLineSet = 0
# typeText = 1
# typePointList = 2
typeMesh = 3
# typeImage = 4
# typeMaterial = 5
# typePeopleSimulation = 6
# typeUnityPackage = 7
# typeSceneNode = 8


n_bytes = 0


def write_data_block_header(size_data, data_id=1, data_type=3, version_data=1):
    """Function to write a DATA BLOCK header.

    Args:
        size_data: data block size (without header)
        data_id: id which is used in the database
        data_type (int): Type of data the data block contains:
            * 0	LineSet	A list of vertices which get connected by line segments
            * 1	Text	A position information and the actual text
            * 2	PointList	A list of 3D points with color information (e.g. point cloud)
            * 3	Mesh	A triangle mesh datastructure️
            * 4	Image	A single of arbitrary format can be stored in this block
            * 5	MaterialStandard	A standard (mesh) material definition
            * 6	SceneNode	A wrapper around a data block which can be used in the scenegraph
            * 7	Track	A track is a tracked position and orientation of an AR device
        version_data: version for this data block

    Returns:

    """

    input_ = [(data_type, 'uint16'),  # data type
              (version_data, 'uint16'),  # version for this data block
              (size_data, 'uint32'),  # data block size (without header)
              (data_id, 'uint64')]  # id which is used in the database

    block_bytes = encode(input_)
    return block_bytes


def encode(input_: list):
    """Encode python objects - normally Python primitives or numpy arrays - into
    its correspondent byte representation

    Args:
        input_ (List[tuples]): List of tuples: (object, type)

    Returns:
        byte: Array of bytes
    """
    global n_bytes
    block = bytearray()

    for tup in input_:
        arr = np.array(tup[0], dtype=tup[1]).tobytes()
        n_bytes += len(arr)
        block += arr

    return block
