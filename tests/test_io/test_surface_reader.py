import pytest
import pandas as pd
from subsurface.io.grids import surface_reader
from subsurface.structs.base_structures import UnstructuredData
import os

input_path = os.path.dirname(__file__)+'/../data'


@pytest.fixture(scope="module")
def get_data() -> UnstructuredData:
    fp = input_path + "/land_surface_vertices.csv"
    unstrdata = surface_reader.read_in_surface_vertices(fp)
    return unstrdata


def test_return_type(get_data):
    assert isinstance(get_data, UnstructuredData)
#
#
# def test_land_surface_vertices_coords(get_vertices):
#     assert get_vertices.iloc[5][2] == 1493.90209961
#     assert get_vertices.iloc[-1][-1] == 2430.35742188