import segyio
from dask.array.tests.test_xarray import xr

from subsurface.structs.base_structures import StructuredData
import matplotlib.pyplot as plt
import segyio
import numpy as np

from tests.conftest import struc_data


def read_in_segy(filepath: str, coords=None) -> StructuredData:

    segyfile = segyio.open(filepath, ignore_geometry=True)
    print(segyfile.unstructured)
    print(segyfile.samples)
    # clip = 1e+2
    # vmin, vmax = -clip, clip

    # Figure
    # figsize = (20, 20)
    # fig, axs = plt.subplots(nrows=1, ncols=1, figsize=figsize, facecolor='w', edgecolor='k',
    #                         squeeze=False,
    #                         sharex=True)
    # axs = axs.ravel()
    # im = axs[0].imshow(segyfile.trace.raw[:].T, cmap=plt.cm.seismic, vmin=vmin, vmax=vmax)
    # plt.show()

    # samples = segyio.tools.collect(segyio.tools.sample_indexes(segyfile))
    # array = segyfile.trace[0]
    array = np.asarray([np.copy(tr) for tr in segyfile.trace[:]])
    print(type(array))
    sd = StructuredData(array)
    # sd.data = samples
    segyfile.close()
    print(sd.data)
    return sd

