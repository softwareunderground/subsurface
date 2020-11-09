from subsurface.structs.base_structures import StructuredData
import matplotlib.pyplot as plt
import numpy as np
try:
    import segyio
    segyio_imported = True
except ImportError:
    segyio_imported = False

from tests.conftest import struc_data


def read_in_segy(filepath: str, coords=None) -> StructuredData:
    """Reader for seismic data stored in sgy/segy files

    Args:
        filepath (str): the path of the sgy/segy file
        coords (dict): If data is a numpy array coords provides the values for
         the xarray dimension. These dimensions are 'x', 'y' and 'z'

    Returns: a StructuredData object with data, the traces with samples written into an xr.Dataset, optionally with
     labels defined by coords

    """

    segyfile = segyio.open(filepath, ignore_geometry=True)
    # plot the seismic profiles
    # clip = 1e+2
    # vmin, vmax = -clip, clip
    #
    # figsize = (20, 20)
    # fig, axs = plt.subplots(nrows=1, ncols=1, figsize=figsize, facecolor='w', edgecolor='k',
    #                         squeeze=False,
    #                         sharex=True)
    # axs = axs.ravel()
    # im = axs[0].imshow(segyfile.trace.raw[:].T, cmap=plt.cm.seismic, vmin=vmin, vmax=vmax)
    # plt.show()

    data = np.asarray([np.copy(tr) for tr in segyfile.trace[:]])

    sd = StructuredData(data) # data holds traces * (samples per trace) values
    segyfile.close()
    return sd

