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
    bytearray_le, header = wells.to_binary()
    print(header)

    with open('well.json', 'w') as outfile:
        json.dump(header, outfile)

    new_file = open("wells.le", "wb")
    new_file.write(bytearray_le)
