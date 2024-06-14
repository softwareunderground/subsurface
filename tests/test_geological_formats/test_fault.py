import pytest
import pandas as pd
from subsurface.modules.reader.faults import faults
from subsurface.core.geological_formats.fault import FaultSticks
import os

input_path = os.path.dirname(__file__)+'/../data/faults'


@pytest.fixture(scope="module")
def get_fault_sticks() -> pd.DataFrame:
    fp = input_path + "/faultsticks"
    faultsticks = faults.read_faultsticks_charisma(fp)
    return faultsticks


def test_fault_sticks_npoints(get_fault_sticks):
    assert len(get_fault_sticks) == 12


def test_fault_sticks_nsticks(get_fault_sticks):
    assert len(get_fault_sticks["stick id"].unique()) == 4


def test_fault_sticks(get_fault_sticks):
    """Test instantiation of FaultSticks class."""
    fault = FaultSticks(get_fault_sticks)