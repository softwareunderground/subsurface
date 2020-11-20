import pytest
from subsurface.io import read_unstruct
import json

@pytest.fixture(scope='module')
def unstruct(data_path):
    us = read_unstruct(data_path + '/interpolator_meshes.nc')
    return us


@pytest.fixture(scope='module')
def wells(data_path):
    us = read_unstruct(data_path + '/wells.nc')
    return us


def test_wells_to_binary(wells):
    vertex = wells.vertex.astype('float32').tobytes()
    cells = wells.cells.astype('int32').tobytes()
    cell_attribute = wells.attributes.values.astype('float32').tobytes()
    vertex_attribute = wells.points_attributes.values.astype('float32').tobytes()
    bytearray_le = vertex + cells + cell_attribute + vertex_attribute
    # print(bytearray_le)

    header = {
        "vertex_shape": wells.vertex.shape,
        "cell_shape": wells.cells.shape,
        "cell_attr_shape": wells.attributes.shape,
        "vertex_attr_shape": wells.points_attributes.shape,
        "cell_attr_names": wells.attributes.columns.to_list(),
        "vertex_attr_names": wells.points_attributes.columns.to_list(),
    }

    print(header)

    with open('well.json', 'w') as outfile:
        json.dump(header, outfile)

    new_file = open("wells.le", "wb")
    new_file.write(bytearray_le)
