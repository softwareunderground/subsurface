import pathlib
from typing import Iterable, Union

import warnings
from subsurface.structs import LineSet
import numpy as np
import pandas as pd
from functools import wraps

from subsurface.structs.base_structures import StructuredData, UnstructuredData

try:
    from welly import Well, Location, Project, Curve
    from striplog import Striplog
    welly_imported = True
except ImportError:
    welly_imported = False


def read_wells(backend='welly'):
    pass


def read_wells_welly(path):
    path_object = pathlib.Path(path)
    file_format = path_object.suffix
    if file_format == '.xlsx' or '.csv':
        WellyToSubsurface()


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
        # Init empty Project

        self.p = Project([])
        self._well_names = set()
        # Init empty well
        self.well = Well(params={'header': {'name': well_name}})
        self.well.location = Location(params={'kb': 100})

    def __repr__(self):
        return self.p

    def add_wells(self, well_names: Iterable):
        new_boreholes = self._well_names.symmetric_difference(well_names)
        self._well_names = self._well_names.union(well_names)
        for b in new_boreholes:
            # TODO: Name and uwi should be different
            w = Well(params={'header': {'name': b, 'uwi': b}})
            w.location = Location(params={'kb': 100})
            self.p += w
        return self.p

    def add_datum(self, data: pd.DataFrame):
        unique_borehole = np.unique(data.index)
        self.add_wells(unique_borehole)

        for b in unique_borehole:
            w = self.p.get_well(b)
            assert data.loc[[b]].shape[1] == 3, 'datum must be XYZ coord'
            w.position = data.loc[[b]].values
        print(w)
        # datum = collars.loc[['foo'], [1, 2, 3]].values
        return self.p

    def add_collar(self, *args, **kwargs):
        """Alias for add_datum"""
        return self.add_datum(*args, **kwargs)

    def add_striplog(self, data: pd.DataFrame):
        unique_borehole = np.unique(data.index)
        self.add_wells(unique_borehole)
        for b in unique_borehole:
            w = self.p.get_well(b)
            data_dict = data.loc[b].to_dict('list')
            s = Striplog.from_dict(data_dict, points=True)
            # step_size = (w.location.md.max() - w.location.md.min()) / w.location.md.shape[0]

            start, stop, step_size = self._calculate_basis_parameters(w, w.location.md.shape[0])
            s_log, basis, table = s.to_log(step_size, start, stop, return_meta=True)

            w.data['lith'] = s
            w.data['lith_log'] = Curve(s_log, basis)

        return self.p

    def add_assays(self, data: pd.DataFrame, basis: Union[str, Iterable]):
        unique_borehole = np.unique(data.index)
        self.add_wells(unique_borehole)
        assay_attributes = data.columns

        if type(basis) == str:
            assay_attributes = assay_attributes.drop(basis)
            basis = data[basis]
        elif type(basis) == Iterable:
            pass
        else:
            raise AttributeError('basis must be either a string with the column name'
                                 'or a array like object')

        for b in unique_borehole:
            for a in assay_attributes:
                w = self.p.get_well(b)
                w.data[a] = Curve(data[a], basis)

        return self.p

    @staticmethod
    def _calculate_basis_parameters(well, n_points):
        """

        Args:
            well:
            n_points:

        Returns:
            start, stop, step
        """
        max_ = well.location.md.max()
        min_ = well.location.md.min()
        step_size = (max_ - min_) / n_points
        return min_ + step_size/2, max_ - step_size/2, step_size + 1e-12

    def add_deviation(self, deviations: pd.DataFrame,
                      td=None,
                      method='mc',
                      update_deviation=True,
                      azimuth_datum=0):
        """
        Add a deviation survey to this instance, and try to compute a position
        log from it.

        Args:
            deviations (pd.DataFrame):
            td
            method
            update_deviation
            azimuth_datum


        """
        unique_borehole = np.unique(deviations.index)
        self.add_wells(unique_borehole)
        for b in unique_borehole:
            w = self.p.get_well(b)
            w.location.add_deviation(deviations.loc[b, ['md', 'inc', 'azi']],
                                             td=td,
                                             method=method,
                                             update_deviation=update_deviation,
                                             azimuth_datum=azimuth_datum)

        return self.p

    def trajectory(self, datum=None, elev=True, points=1000, **kwargs):
        """
        Get regularly sampled well trajectory. Assumes there is a position
        log already, e.g. resulting from calling `add_deviation()` on a
        deviation survey.

        Args:
            datum (array-like): A 3-element array with adjustments to (x, y, z).
                For example, the x-position, y-position, and KB of the tophole
                location. This is also known as collar of the borehole.
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
                                             points=points,
                                             **kwargs)

    def to_subsurface(self, datum=None, elev=True,
                      n_points=1000,
                      return_element=False,
                      convert_lith = True,
                      attributes=None,
                      **kwargs):
        """Method to convert well data to `subsurface.UnstructuredData`

        Parameters
        ----------
        datum
        elev
        n_points
        kwargs

        Returns
        -------

        """
        vertex = np.zeros((0,3))
        edges = np.zeros((0, 2), dtype=np.int_)
        attributes = pd.DataFrame(columns=self.p.uwis)
        last_index = 0
        for w in self.p.get_wells():

            xyz = w.location.trajectory(None, elev, n_points, **kwargs)

            # Make sure deviation is there
            a = np.arange(0 + last_index, xyz.shape[0] - 1 + last_index, dtype=np.int_)
            b = np.arange(1 + last_index, xyz.shape[0] + last_index, dtype=np.int_)
            last_index += xyz.shape[0]
            edges_b = np.vstack([a, b]).T

            vertex = np.vstack((vertex, xyz))
            edges = np.vstack((edges, edges_b))

            # Change curve basis
            start, stop, step_size = self._calculate_basis_parameters(w, n_points)
            basis = np.arange(start, stop, step_size)
            w.unify_basis(keys=None, basis=basis)

            # Convert striplog into Curve
            if convert_lith is True:
                try:
                    start, stop, step_size = self._calculate_basis_parameters(w, n_points-1)
                    s_log, basis, table = w.data['lith'].to_log(step_size, start, stop, return_meta=True)

                    w.data['lith_log'] = Curve(s_log, basis)
                except KeyError:
                    warnings.warn(f'No lith curve in this borehole {w.name}. Setting values'
                                  'to 0')

                    w.data['lith_log'] = Curve(np.zeros(n_points-1))

        unstructured_data = UnstructuredData(
            vertex,
            edges,
            self.p.df()
        )

        if return_element is True:
            return LineSet(unstructured_data)
        else:
            return unstructured_data
