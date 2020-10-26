from typing import List

import pytest
import os

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
