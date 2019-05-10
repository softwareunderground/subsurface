import pytest
from subsurface.io import from_segy
from subsurface import Seismic


def test_from_segy():
    seismic = from_segy("tests/data/test.segy")
    assert type(seismic) == Seismic