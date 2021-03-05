from io import StringIO
from typing import Union

import pandas as pd

from subsurface.structs import UnstructuredData
from subsurface.reader.wells import read_collar


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
        cells_attributes=collars_attributes.astype('float32'),
        xarray_attributes={"wells_names": wells_names.values.tolist()})  # TODO: This should be int16!

    return ud
