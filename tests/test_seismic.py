import pytest
from subsurface.seismic import Seismic, from_segy
from subsurface import units
import xarray.testing
import numpy.testing

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

def test_seismic_units():
    """Test creating Seismic instance from SEGY file."""
    seismic = from_segy("tests/data/test.segy")
    assert seismic.units == units.dimensionless

def test_seismic_unit_setting():
    """Test creating Seismic instance from SEGY file."""
    seismic = from_segy("tests/data/test.segy")
    seismic.set_units(units.km/units.s)
    assert str(seismic.units) == (units.km / units.s)

def test_seismic_unit_conversion():
    """Test creating Seismic instance from SEGY file."""
    seismic = from_segy("tests/data/test.segy")
    seismic_mod = from_segy("tests/data/test.segy")
    seismic.set_units(units.km/units.s)
    seismic_mod.set_units(units.km/units.s)
    #assert xarray.testing.assert_equal(seismic, seismic_mod)
    numpy.testing.assert_array_equal(seismic.values,seismic_mod.values)
    seismic_mod.convert_units(units.m / units.s)
    a, b = seismic.values.copy(), seismic_mod.values.copy()
    b /= 1e3
    numpy.testing.assert_allclose(a, b, rtol=1e-6)
    seismic_mod.convert_units(units.km / units.s)
    b = seismic_mod.values.copy()
    numpy.testing.assert_allclose(a, b, rtol=1e-6)
