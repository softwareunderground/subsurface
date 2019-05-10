import pytest
from subsurface import Seismic, from_segy
import numpy as np
import segyio


@pytest.fixture(scope="module")
def seismic():
    """Benchmark Seismic object."""
    # coords = [{"x": np.arange(10)}, {"y": np.arange(10)}, {"z": np.arange(100)}]
    coords = [("x", np.arange(10)), ("y", np.arange(10)), ("z", np.arange(100))]
    cube = segyio.tools.cube("tests/data/test.segy")
    # seis = from_segy("tests/data/test.segy")
    return Seismic(cube, coords=coords)


def test_from_segy():
    """Test creating Seismic instance from SEGY file."""
    seismic = from_segy("tests/data/test.segy")
    assert type(seismic) == Seismic


def test_getitem(seismic):
    assert type(seismic.loc[:,:,50]) == Seismic