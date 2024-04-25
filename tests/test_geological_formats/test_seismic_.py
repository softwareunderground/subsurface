import pytest

from conftest import RequirementsLevel, check_requirements
from subsurface import optional_requirements
from subsurface.geological_formats.seismic import Seismic, from_segy
import numpy as np



@pytest.mark.skipif(check_requirements(RequirementsLevel.OPTIONAL), reason="Geopandas is not imported ")
def test_seismic():
    """Benchmark Seismic object."""
    coords = [("x", np.arange(10)), ("y", np.arange(10)), ("z", np.arange(100))]
    segyio = optional_requirements.require_segyio()
    cube = segyio.tools.cube("../data/segy/test.segy")
    
    # ? What is the difference of this? Should we delete it?
    seismic = Seismic(cube, coords=coords)
    seismic2 = from_segy("../data/segy/test.segy")
