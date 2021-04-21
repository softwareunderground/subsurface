from typing import List

import warnings

from subsurface.reader.wells.pandas_to_welly import WellyToSubsurfaceHelper
import numpy as np

from subsurface.structs.base_structures import UnstructuredData

from welly import Well, Location, Project, Curve
from striplog import Striplog, Component


__all__ = ['welly_to_subsurface', 'striplog_to_curve_log',
           'change_curve_basis_to_n_vertex_per_well_inplace',
           'vertex_and_cells_from_welly_trajectory',
           'well_without_valid_survey']


def welly_to_subsurface(wts: WellyToSubsurfaceHelper,
                        elev=True,
                        n_vertex_per_well=50,
                        convert_lith=True,
                        table: List[Component] = None,
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

        change_curve_basis_to_n_vertex_per_well_inplace(n_vertex_per_well, w, wts)

        # Convert striplog into Curve
        if convert_lith is True and 'lith' in w.data:
            if table is None: table = wts.lith_component_table
            w.data['lith_log'] = striplog_to_curve_log(n_vertex_per_well, table, w, wts)

    try:
        df = wts.p.df()
    except ValueError as e:
        if 'objects passed' in str(e):
            df = None
        else:
            raise ValueError

    print('The following boreholes failed being processed: ', missed_wells)

    unstructured_data = UnstructuredData.from_array(vertex, cells, df)
    return unstructured_data


def striplog_to_curve_log(n_vertex_per_well, table, w: Well, wts: WellyToSubsurfaceHelper) -> Curve:
    start, stop, step_size = wts._calculate_basis_parameters(w, n_vertex_per_well - 1)
    s_log, basis, _table = w.data['lith'].to_log(step_size, start, stop, table=table, return_meta=True)
    return Curve(s_log, basis)


def change_curve_basis_to_n_vertex_per_well_inplace(n_points, w, wts):
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
