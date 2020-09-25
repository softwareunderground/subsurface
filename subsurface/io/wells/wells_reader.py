from subsurface.structs import LineSet
import numpy as np
import pandas as pd
from functools import wraps

from subsurface.structs.base_structures import StructuredData, UnstructuredData

try:
    from welly import Well, Location
    welly_imported = True
except ImportError:
    welly_imported = False


class WellyToSubsurface:
    def __init__(self, well_name: str = None):
        """ Class that wraps `welly` to read borehole data - las files
         and deviations - and converts it into a `subsurface.mesh`

        This class is only meant to be extended with all the necessary functionality
         to load borehole data. For extensive manipulations of the data
         it should be done in `welly` itself.

        We need a class because it is going to be quite difficult to make
         one single function that fits all

        A borehole has:

            - [ ] Datum (XYZ location)

            - [X] Deviation

            - [ ] Lithology: For this we are going to need striplog

            - [ ] Logs

        Everything would be a LineSet with a bunch of properties

        Parameters
        ----------
        well_name (str): Name of the borehole

        Notes
        -----


        TODO: I think welly can initialize a Well from a file. That would be
         something to consider later on

        """

        # Init empty well
        self.well = Well(params={'header': {'name': well_name}})
        self.well.location = Location(params={'kb':100})

    def add_deviation(self, deviation,
                      td=None,
                      method='mc',
                      update_deviation=True,
                      azimuth_datum=0):
        """
        Add a deviation survey to this instance, and try to compute a position
        log from it.

        Parameters
        ----------
        deviation (numpy.ndarray[n,3])
        td
        method
        update_deviation
        azimuth_datum
        """
        return self.well.location.add_deviation(deviation,
                      td=td,
                      method=method,
                      update_deviation=update_deviation,
                      azimuth_datum=azimuth_datum)

    def trajectory(self, datum=None, elev=True, points=1000, **kwargs):
        """
        Get regularly sampled well trajectory. Assumes there is a position
        log already, e.g. resulting from calling `add_deviation()` on a
        deviation survey.

        Args:
            datum (array-like): A 3-element array with adjustments to (x, y, z).
                For example, the x-position, y-position, and KB of the tophole
                location.
            elev (bool): In general the (x, y, z) array of positions will have
                z as TVD, which is positive down. If `elev` is True, positive
                will be upwards.
            points (int): The number of points in the trajectory.
            kwargs: Will be passed to `scipy.interpolate.splprep()`.

        Returns:
            ndarray. An array with shape (`points` x 3) representing the well
                trajectory. Columns are (x, y, z).
        """
        return self.well.location.trajectory(datum=datum, elev=elev,
                                             points=points, **kwargs)

    def to_subsurface(self, datum=None, elev=True, points=1000,
                      return_element=False,
                      **kwargs):
        """Method to convert well data to `subsurface.UnstructuredData`

        Parameters
        ----------
        datum
        elev
        points
        kwargs

        Returns
        -------

        """
        XYZ_points = self.trajectory(datum, elev, points, **kwargs)

        # Make sure deviation is there
        a = np.arange(0, XYZ_points.shape[0] - 1, dtype=np.int_)
        b = np.arange(1, XYZ_points.shape[0], dtype=np.int_)
        edges = np.vstack([a, b]).T

        # Default isinstantiation with automatic segment generation
        unstructured_data = UnstructuredData(
            XYZ_points,
            edges,
            #pd.DataFrame(np.ones(edges.shape[0]), columns=['nan'])
        )

        if return_element is True:
            return LineSet(unstructured_data)
        else:
            return unstructured_data
