import pytest
import pandas as pd
from subsurface.io.grids import land_surface_vertices
import os

input_path = os.path.dirname(__file__)+'/../data'


@pytest.fixture(scope="module")
def get_vertices() -> pd.DataFrame:
    fp = input_path + "/land_surface_vertices.csv"
    vertices = land_surface_vertices.read_in_land_surface_vertices(fp)
    return vertices


def test_land_surface_vertices_nrows(get_vertices):
    assert len(get_vertices) == 413250


def test_land_surface_vertices_coords(get_vertices):
    assert get_vertices.iloc[5][2] == 1493.90209961
    assert get_vertices.iloc[-1][-1] == 2430.35742188
