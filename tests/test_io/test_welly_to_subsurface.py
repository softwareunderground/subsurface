import pytest

import subsurface as ss
import pandas as pd
import numpy as np
welly = pytest.importorskip('welly')


def test_welly_to_subsurface():
    wts = ss.io.WellyToSubsurface('test_well')

    dev = pd.DataFrame(np.array([[0, 0, 0],
                                 [2133, 0, 0]]),
                       columns=['Depth', 'Dip', 'Azimuth'])

    # In a well we can have deviation
    wts.add_deviation(dev[['Depth', 'Dip', 'Azimuth']].values)
    XYZ = wts.trajectory()
    assert np.testing.assert_almost_equal(XYZ[355:357],
                                          np.array([[0., 0., -757.97297297],
                                                    [0., 0., -760.10810811]]))

    # Datum (XYZ location)

    # Lithology

    # Logs

    # Everything would be a LineSet with a bunch of properties
    wts.to_subsurface()


