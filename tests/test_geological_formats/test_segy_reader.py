from typing import List

import pytest
import os

from subsurface import StructuredGrid
from subsurface.geological_formats import segy_reader
from subsurface.structs.base_structures import StructuredData

input_path = os.path.dirname(__file__) + '/../data/segy'
files = ['/E5_MIG_DMO_FINAL.sgy', '/E5_MIG_DMO_FINAL_DEPTH.sgy', '/E5_STACK_DMO_FINAL.sgy', '/test.segy']
# all files are unstructured: only raw data reading and writing is supported by segyio


@pytest.fixture(scope="module")
def get_structured_data() -> List[StructuredData]:
    file_array = [input_path + x for x in files]
    sd_array = [segy_reader.read_in_segy(fp) for fp in file_array]
    return sd_array


def test_converted_to_structured_data(get_structured_data):
    for x in get_structured_data:
        # print(x.data.items())
        assert isinstance(x, StructuredData)


def test_pyvista_structured_grid(get_structured_data):
    from subsurface.visualization import to_pyvista_grid
    from subsurface.visualization import pv_plot
    # StructuredData from Dataset
    for x in get_structured_data:
        sg = StructuredGrid(x)
        s = to_pyvista_grid(sg, 'data') # works only for test.segy as x.shape == y.shape so the test fails here
        pv_plot([s], image_2d=True)
