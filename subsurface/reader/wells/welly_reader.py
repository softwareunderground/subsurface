from typing import List

import warnings

from subsurface.reader.readers_data import ReaderWellsHelper
from subsurface.reader.wells.pandas_to_welly import WellyToSubsurface
from subsurface.reader.wells.well_files_reader import read_borehole_files
from subsurface.structs import LineSet
import numpy as np
import pandas as pd

from subsurface.structs.base_structures import UnstructuredData

try:
    from welly import Well, Location, Project, Curve
    from striplog import Striplog

    welly_imported = True
except ImportError:
    welly_imported = False


def welly_to_subsurface(wts: WellyToSubsurface,
                        elev=True,
                        n_vertex_per_well=50,
                        convert_lith=True,
                        table=None,
                        **kwargs) -> UnstructuredData:
    """Method to convert well data to `subsurface.UnstructuredData`

    Args:
        elev (bool): In general the (x, y, z) array of positions will have
            z as TVD, which is positive down. If `elev` is True, positive
            will be upwards.
        n_vertex_per_well (int): Number of vertex used to describe the geometry of the
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
    for w in wts.p.get_wells():
        if well_without_valid_survey(w, missed_wells): continue

        cells, vertex, last_index = vertex_and_cells_from_welly_trajectory(
            cells, elev, kwargs, last_index, n_vertex_per_well, vertex, w)

        change_curve_basis_to_n_vertex_per_well(n_vertex_per_well, w, wts)

        # Convert striplog into Curve
        if convert_lith is True and 'lith' in w.data:
            striplog_to_curve_log(n_vertex_per_well, table, w, wts)
            # try:
            #
            # except KeyError:
            #     warnings.warn(
            #         f'No lith curve in this borehole {w.name}. Setting values'
            #         'to 0')
            #
            #     w.data['lith_log'] = Curve(np.zeros(n_vertex_per_well - 1))

    try:
        df = wts.p.df()
    except ValueError as e:
        if 'objects passed' in str(e):
            df = None
        else:
            raise ValueError

    print('The following boreholes failed being processed: ', missed_wells)

    unstructured_data = UnstructuredData.from_array(vertex, cells, df)

    # if return_element is True:
    #     return LineSet(unstructured_data)
    # else:
    return unstructured_data


def striplog_to_curve_log(n_vertex_per_well, table, w, wts):
    start, stop, step_size = wts._calculate_basis_parameters(w, n_vertex_per_well - 1)
    s_log, basis, _table = w.data['lith'].to_log(step_size,
                                                 start,
                                                 stop,
                                                 table=table,
                                                 return_meta=True)
    w.data['lith_log'] = Curve(s_log, basis)


def change_curve_basis_to_n_vertex_per_well(n_points, w, wts):
    start, stop, step_size = wts._calculate_basis_parameters(w, n_points)
    basis = np.arange(start, stop, step_size)
    w.unify_basis(keys=None, basis=basis)


def vertex_and_cells_from_welly_trajectory(cells: np.ndarray, elev: bool,
                                           welly_trajectory_kwargs: dict,
                                           last_index: int, n_vertex_for_well: int,
                                           vertex: np.ndarray, w: Well):
    xyz = w.location.trajectory(w.position, elev, n_vertex_for_well, **welly_trajectory_kwargs)
    # Make sure deviation is there
    a = np.arange(0 + last_index, xyz.shape[0] - 1 + last_index, dtype=np.int_)
    b = np.arange(1 + last_index, xyz.shape[0] + last_index, dtype=np.int_)
    cells_b = np.vstack([a, b]).T

    vertex = np.vstack((vertex, xyz))
    cells = np.vstack((cells, cells_b))
    last_index += xyz.shape[0]

    return cells, vertex, last_index


def well_without_valid_survey(w: Well, missed_wells: List[str]):
    well_without_position = w.location.position is None
    if well_without_position:
        warnings.warn(f'At least one of the wells do not have '
                      'assigned a survey. Borehole name: {w.name}')
        missed_wells.append(w.name)
    return well_without_position
# def pandas_to_welly(
#         wts: WellyToSubsurface = None,
#         collar_df: pd.DataFrame = None,
#         survey_df: pd.DataFrame = None,
#         lith_df: pd.DataFrame = None,
#         attrib_dfs: List[pd.DataFrame] = None
# ):
#     # Init WellyToSubsurface object
#     if wts is None: wts = WellyToSubsurface()
#
#     if collar_df is not None: wts.add_datum(collar_df)
#     if survey_df is not None: wts.add_deviation(survey_df)
#     if lith_df is not None:  wts.add_striplog(lith_df)
#
#     # First check if is just a path or list
#     if attrib_dfs is not None:
#         for e, attrib in enumerate(attrib_dfs):
#             wts.add_assays(attrib, basis='basis')
#     return wts
#
#
# def read_to_welly(reader_wells_helper: ReaderWellsHelper, wts: WellyToSubsurface = None):
#     dfs = read_borehole_files(reader_wells_helper)
#     wts = pandas_to_welly(wts, **dfs)
#
#     return wts
