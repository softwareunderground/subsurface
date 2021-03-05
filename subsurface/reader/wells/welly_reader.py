import io
import pathlib
from typing import Iterable, Union, List, Optional

import warnings

from subsurface.reader.wells.well_files_reader import read_borehole_files
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


class WellyToSubsurface:
    def __init__(self, well_name: str = None):
        """ Class that wraps `welly` to read borehole data - las files
         and deviations, csv, excel - and converts it into a
         `subsurface.UnstructuredData`

        This class is only meant to be extended with all the necessary functionality
         to load borehole data. For extensive manipulations of the data
         it should be done in `welly` itself.

        We need a class because it is going to be quite difficult to make
         one single function that fits all

        A borehole has:

            -  Datum (XYZ location)

            -  Deviation

            - Lithology: For this we are going to need striplog

            - Logs

        Everything would be a LineSet with a bunch of properties

        Parameters
        ----------
        well_name (Optional[str]): Name of the borehole

        Notes
        -----


        TODO: I think welly can initialize a Well from a file. That would be
         something to consider later on

        """
        # Init empty Project
        if welly_imported is False:
            raise ImportError('You need to install welly to read well data.')

        self.p = Project([])
        self._well_names = set()
        # Init empty well
        self.well = Well(params={'header': {'name': well_name}})
        self.well.location = Location(params={'kb': 100})

    def __repr__(self):
        return self.p.__repr__()

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
            datum = data.loc[[b]]
            assert datum.shape[1] == 3, 'datum must be XYZ coord'
            w.position = datum.values[0]

        return self.p

    def add_collar(self, *args, **kwargs):
        """Alias for add_datum"""
        return self.add_datum(*args, **kwargs)

    def add_striplog(self, data: pd.DataFrame):
        unique_borehole = np.unique(data.index)
        self.add_wells(unique_borehole)
        missed_borehole = []
        for b in unique_borehole:
            w = self.p.get_well(b)
            data_dict = data.loc[[b]].to_dict('list')

            s = Striplog.from_dict(data_dict, points=True)

            try:
                n_basis = w.location.md.shape[0]
            except TypeError:
                n_basis = 2
            try:
                start, stop, step_size = self._calculate_basis_parameters(
                    w,
                    n_basis)
                s_log, basis, table = s.to_log(step_size, start, stop,
                                               return_meta=True)

                w.data['lith'] = s
                w.data['lith_log'] = Curve(s_log, basis)
            except TypeError:
                missed_borehole.append(b)
                continue

        print('The following striplog failed being processed: ', missed_borehole)

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

        max_ = well.location.md.max()
        min_ = well.location.md.min()
        step_size = (max_ - min_) / n_points
        return min_ + step_size / 2, max_ - step_size / 2, step_size + 1e-12

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
            w.location.add_deviation(deviations.loc[[b], ['md', 'inc', 'azi']],
                                     td=td,
                                     method=method,
                                     update_deviation=update_deviation,
                                     azimuth_datum=azimuth_datum)
            if w.location.position is None:
                raise ValueError('Deviations could not be calculated.')

        return self.p

    # TODO: Unused?
    def _trajectory(self, datum=None, elev=True, points=1000, **kwargs):
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

    def to_subsurface(self,
                      elev=True,
                      n_points=50,
                      return_element=False,
                      convert_lith=True,
                      table=None,
                      **kwargs):
        """Method to convert well data to `subsurface.UnstructuredData`

        Args:
            elev (bool): In general the (x, y, z) array of positions will have
                z as TVD, which is positive down. If `elev` is True, positive
                will be upwards.
            n_points (int): Number of vertex used to describe the geometry of the
             well.
            return_element (bool): if True return a `subsurface.LineSet` instead
            convert_lith (bool): if True convert lith from stiplog to curve
            table (List[Striplog.Component]): List of components to map lithologies
             to value.
            **kwargs:
                `Well.location.trajectory` kwargs

        Returns:

        """
        vertex = np.zeros((0, 3))
        cells = np.zeros((0, 2), dtype=np.int_)

        last_index = 0
        missed_wells = []
        for w in self.p.get_wells():
            if w.location.position is None:
                warnings.warn('At least one of the wells do not have '
                              'assigned a survey. Borehole name: ' + w.name)
                missed_wells.append(w.name)
                continue

            xyz = w.location.trajectory(w.position, elev, n_points, **kwargs)

            # Make sure deviation is there
            a = np.arange(0 + last_index, xyz.shape[0] - 1 + last_index,
                          dtype=np.int_)
            b = np.arange(1 + last_index, xyz.shape[0] + last_index, dtype=np.int_)
            last_index += xyz.shape[0]
            cells_b = np.vstack([a, b]).T

            vertex = np.vstack((vertex, xyz))
            cells = np.vstack((cells, cells_b))

            # Change curve basis
            start, stop, step_size = self._calculate_basis_parameters(w, n_points)
            basis = np.arange(start, stop, step_size)
            w.unify_basis(keys=None, basis=basis)

            # Convert striplog into Curve
            if convert_lith is True and 'lith' in w.data:
                try:
                    start, stop, step_size = self._calculate_basis_parameters(w,
                                                                              n_points - 1)
                    s_log, basis, _table = w.data['lith'].to_log(step_size,
                                                                 start,
                                                                 stop,
                                                                 table=table,
                                                                 return_meta=True)

                    w.data['lith_log'] = Curve(s_log, basis)
                except KeyError:
                    warnings.warn(
                        f'No lith curve in this borehole {w.name}. Setting values'
                        'to 0')

                    w.data['lith_log'] = Curve(np.zeros(n_points - 1))

        try:
            df = self.p.df()
        except ValueError as e:
            if 'objects passed' in str(e):
                df = None
            else:
                raise ValueError

        print('The following boreholes failed being processed: ', missed_wells)

        unstructured_data = UnstructuredData.from_array(vertex, cells, df)

        if return_element is True:
            return LineSet(unstructured_data)
        else:
            return unstructured_data


def pandas_to_welly(
        wts: WellyToSubsurface = None,
        collar_df: pd.DataFrame = None,
        survey_df: pd.DataFrame = None,
        lith_df: pd.DataFrame = None,
        attrib_dfs: List[pd.DataFrame] = None
):
    # Init WellyToSubsurface object
    if wts is None:
        wts = WellyToSubsurface()

    if collar_df is not None:
        wts.add_datum(collar_df)

    if survey_df is not None:
        wts.add_deviation(survey_df)

    if lith_df is not None:
        wts.add_striplog(lith_df)

    # First check if is just a path or list
    if attrib_dfs is not None:
        for e, attrib in enumerate(attrib_dfs):
            wts.add_assays(attrib, basis='basis')
    return wts


def read_to_welly(
        collar_file: str = None,
        survey_file: str = None,
        lith_file: str = None,
        attrib_file: Union[str, List] = None,
        wts: WellyToSubsurface = None,
        read_collar_kwargs=None,
        read_survey_kwargs=None,
        read_lith_kwargs=None,
        read_attributes_kwargs=None,

):
    dfs = read_borehole_files(
        collar_file,
        survey_file,
        lith_file,
        attrib_file,
        read_collar_kwargs,
        read_survey_kwargs,
        read_lith_kwargs,
        read_attributes_kwargs)

    wts = pandas_to_welly(wts, **dfs)

    return wts
