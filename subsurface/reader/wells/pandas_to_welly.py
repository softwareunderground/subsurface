from typing import Iterable, Union, List

import numpy as np
import pandas as pd

try:
    from welly import Well, Location, Project, Curve
    from striplog import Striplog, Component

    welly_imported = True
except ImportError:
    welly_imported = False


__all__ = ['WellyToSubsurfaceHelper', ]


class WellyToSubsurfaceHelper:
    def __init__(self,
                 collar_df: pd.DataFrame = None,
                 survey_df: pd.DataFrame = None,
                 lith_df: pd.DataFrame = None,
                 attrib_dfs: List[pd.DataFrame] = None):
        """ Class that wraps `welly` to read borehole data - las files (upcoming)
         and deviations, csv, excel - and converts it into a
         `subsurface.UnstructuredData`

        This class is only meant to be extended with all the necessary functionality
         to load borehole data. For extensive manipulations of the data
         it should be done in `welly` itself.

        A borehole has:

            -  Datum (XYZ location)

            -  Deviation

            - Lithology: For this we are going to need striplog

            - Logs

        Everything would be a LineSet with a bunch of properties

        """

        if welly_imported is False:
            raise ImportError('You need to install welly to read well data.')

        self.p = Project([])
        self._well_names = set()
        self._unique_formations = None

        if collar_df is not None: self.add_datum(collar_df)
        if survey_df is not None: self.add_deviation(survey_df)
        if lith_df is not None:  self.add_striplog(lith_df)

        # First check if is just a path or list
        if attrib_dfs is not None:
            for e, attrib in enumerate(attrib_dfs):
                self.add_assays(attrib, basis='basis')

    def __repr__(self):
        return self.p.__repr__()

    @property
    def lith_component_table(self):
        return [Component({'lith': l}) for l in self._unique_formations]

    @lith_component_table.setter
    def lith_component_table(self, unique_formations):
        self._unique_formations = unique_formations

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
        self.lith_component_table = data['component lith'].unique()
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
        """ Add a deviation survey to this instance, and try to compute a position
         log from it.

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
