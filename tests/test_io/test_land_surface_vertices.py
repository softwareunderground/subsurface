import pytest
import pandas as pd
from subsurface.io.grids import land_surface_vertices
from subsurface.io.grids.land_surface_vertices import read_in_land_surface_vertices
import os

input_path = os.path.dirname(__file__)+'/../data'

@pytest.fixture(scope="module")
def get_vertices() -> pd.DataFrame:
    fp = input_path + "/land_surface_vertices.csv"
    return fp

def test_land_surface_vertices_nrows(get_vertices):
    assert len(read_in_land_surface_vertices(get_vertices)) == 413250