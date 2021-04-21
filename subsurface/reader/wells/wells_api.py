from typing import List

import pandas as pd
from striplog import Component

from subsurface.reader.wells.pandas_to_welly import WellyToSubsurfaceHelper
from subsurface.reader.wells.well_files_reader import read_borehole_files
from subsurface.reader.wells.welly_reader import welly_to_subsurface
from subsurface.reader.readers_data import ReaderWellsHelper, ReaderFilesHelper

from subsurface.structs import UnstructuredData

from subsurface.reader.wells import read_collar


__all__ = ['read_wells_to_unstruct', 'borehole_location_to_unstruct']


def read_wells_to_unstruct(reader_wells_helper: ReaderWellsHelper,
                            backend='welly', n_vertex_per_well=80,
                           table: List[Component] = None) -> UnstructuredData:
    """Read from csv files (or excel) to `subsurface.Unstructured` object.

    Args:
        backend (string): Which library use for reading and processing of data.
         So far: welly
        table (List[Striplog.Component]): List of components to map lithologies
         to value.
        n_vertex_per_well (int): Number of vertex used to describe the geometry of the
         well.

    Returns:
        `subsurface.UnstructuredData`:  if `return_welly` also the
         welly object

    """
    pandas_dict = read_borehole_files(reader_wells_helper)

    if backend == 'welly':
        wts = WellyToSubsurfaceHelper(**pandas_dict)
        unstruct = welly_to_subsurface(wts, n_vertex_per_well=n_vertex_per_well, table=table)
    else:
        raise AttributeError('Only welly is available at the moment')

    return unstruct


def borehole_location_to_unstruct(reader_helper: ReaderFilesHelper,
                                  add_number_segments: bool = True) -> UnstructuredData:

    collars = read_collar(reader_helper)
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
