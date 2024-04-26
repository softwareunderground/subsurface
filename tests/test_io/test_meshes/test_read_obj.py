import pytest
import pyvista as pv
from dotenv import dotenv_values

from conftest import RequirementsLevel

config = dotenv_values()
path_to_obj = config.get('PATH_TO_OBJ')
path_to_mtl = config.get('PATH_TO_MTL')


@pytest.mark.skipif(
    condition=(RequirementsLevel.MESH | RequirementsLevel.PLOT) not in RequirementsLevel.REQUIREMENT_LEVEL_TO_TEST(),
    reason="Need to set the READ_MESH variable to run this test"
)
def test_read_obj():
    reader = pv.get_reader(path_to_obj)
    mesh = reader.read()
    mesh.plot()
    
    