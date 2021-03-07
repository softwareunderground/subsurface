from io import StringIO
from typing import Union

import pandas as pd

from subsurface.reader.wells.pandas_to_welly import WellyToSubsurface
from subsurface.reader.wells.well_files_reader import read_borehole_files
from subsurface.reader.wells.welly_reader import welly_to_subsurface
from subsurface.reader.readers_data import ReaderWellsHelper

from subsurface.structs import UnstructuredData

from subsurface.reader.wells import read_collar

#
# def read_wells_to_unstruct(backend='welly', n_points=1000,
#                            return_welly=False, **kwargs):
#     """Read from csv files (or excel) to `subsurface.Unstructured` object.
#
#     Args:
#         backend (string): Which library use for reading and processing of data.
#          So far: welly
#         n_points (int): Number of vertex used to describe the geometry of the
#          well.
#         return_welly (bool): If True return also the welly project object.
#
#         **kwargs:
#          `subsurface.reader.wells.read_wells` args
#
#     Returns:
#         `subsurface.UnstructuredData`:  if `return_welly` also the
#          welly object
#
#     Examples:
#         >>> unstructured_data = read_wells_to_unstruct(
#                 collar_file=data_path.joinpath('borehole_collar.xlsx'),
#                 read_collar_kwargs={'usecols': [0, 1, 2, 4]},
#                 survey_file=data_path.joinpath('borehole_survey.xlsx'),
#                 read_survey_kwargs={
#                     'columns_map': {'DEPTH': 'md', 'INCLINATION': 'inc',
#                                     'DIRECTION': 'azi'},
#                     'index_map': {'ELV-01': 'foo', 'ELV-02': 'bar'}
#                 },
#                 lith_file=data_path.joinpath('borehole_lith.xlsx'),
#                 read_lith_kwargs={
#                     'index_col': 'SITE_ID',
#                     'columns_map': {'DEPTH_FROM': 'top',
#                                     'DEPTH_TO': 'base',
#                                     'LITHOLOGY': 'component lith',
#                                     'SITE_ID': 'description'}
#                 },
#                 attrib_file=[data_path.joinpath('borehole_assays.xlsx'),
#                              data_path.joinpath('borehole_density.xlsx')],
#                 read_attributes_kwargs={
#                     'drop_cols': ['TO', 'LITOLOGIA'],
#                     'columns_map': [
#                         {'FROM': 'basis'},
#                         {'DEPTH_TO': 'basis'}
#                     ]
#                 }
#             )
#     """
#     if backend == 'welly':
#         table = kwargs.pop("table", None)
#         wts = read_to_welly(**kwargs)
#         unstruct = wts.welly_to_subsurface(n_vertex_per_well=n_points, table=table)
#         s = (unstruct, wts.p) if return_welly is True else unstruct
#
#     else:
#         raise AttributeError('Only welly is available at the moment')
#
#     return s


def read_wells_to_unstruct(reader_wells_helper: ReaderWellsHelper,
                            backend='welly', n_vertex_per_well=1000, return_welly=False, **kwargs) -> UnstructuredData:
    """Read from csv files (or excel) to `subsurface.Unstructured` object.

    Args:
        backend (string): Which library use for reading and processing of data.
         So far: welly
        n_points (int): Number of vertex used to describe the geometry of the
         well.
        return_welly (bool): If True return also the welly project object.

        **kwargs:
         `subsurface.reader.wells.read_wells` args

    Returns:
        `subsurface.UnstructuredData`:  if `return_welly` also the
         welly object

    Examples:
        >>> unstructured_data = read_wells_to_unstruct(
                collar_file=data_path.joinpath('borehole_collar.xlsx'),
                read_collar_kwargs={'usecols': [0, 1, 2, 4]},
                survey_file=data_path.joinpath('borehole_survey.xlsx'),
                read_survey_kwargs={
                    'columns_map': {'DEPTH': 'md', 'INCLINATION': 'inc',
                                    'DIRECTION': 'azi'},
                    'index_map': {'ELV-01': 'foo', 'ELV-02': 'bar'}
                },
                lith_file=data_path.joinpath('borehole_lith.xlsx'),
                read_lith_kwargs={
                    'index_col': 'SITE_ID',
                    'columns_map': {'DEPTH_FROM': 'top',
                                    'DEPTH_TO': 'base',
                                    'LITHOLOGY': 'component lith',
                                    'SITE_ID': 'description'}
                },
                attrib_file=[data_path.joinpath('borehole_assays.xlsx'),
                             data_path.joinpath('borehole_density.xlsx')],
                read_attributes_kwargs={
                    'drop_cols': ['TO', 'LITOLOGIA'],
                    'columns_map': [
                        {'FROM': 'basis'},
                        {'DEPTH_TO': 'basis'}
                    ]
                }
            )
    """
    pandas_dict = read_borehole_files(reader_wells_helper)

    if backend == 'welly':
        table = kwargs.pop("table", None)
        # wts = read_to_welly(**kwargs)
        wts = WellyToSubsurface(None, **pandas_dict)
        unstruct = welly_to_subsurface(wts, n_vertex_per_well=n_vertex_per_well, table=table)
    else:
        raise AttributeError('Only welly is available at the moment')

    return unstruct


def borehole_location_to_unstruct(
        collar_file: Union[str, StringIO],
        read_collar_kwargs: dict = None,
        add_number_segments: bool = True) -> UnstructuredData:
    if read_collar_kwargs is None:
        read_collar_kwargs = dict()

    collars = read_collar(collar_file, **read_collar_kwargs)
    collars_attributes = pd.DataFrame()

    # Remove duplicates
    collars_single_well = collars[~collars.index.duplicated()]
    wells_names = collars_single_well.index

    if add_number_segments is True:
        number_of_segments = collars.index.value_counts(sort=False).values
        collars_attributes['number_segments'] = number_of_segments

    ud = UnstructuredData.from_array(
        vertex=collars_single_well[['x', 'y', 'altitude']].values.astype('float32'),
        cells="points",
        cells_attr=collars_attributes.astype('float32'),
        xarray_attributes={"wells_names": wells_names.values.tolist()})  # TODO: This should be int16!

    return ud