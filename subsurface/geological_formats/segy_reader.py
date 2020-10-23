import segyio
from subsurface.structs.base_structures import StructuredData
import matplotlib.pyplot as plt
import segyio


def read_in_segy(filepath: str, coords=None) -> StructuredData:

    segyfile = segyio.open(filepath, ignore_geometry=True)
    samples = segyio.tools.collect(segyio.tools.sample_indexes(segyfile))
    sd = StructuredData(samples, coords)
    return sd

