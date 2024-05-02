import numpy as np
import warnings

from subsurface.core.reader_helpers.readers_data import GenericReaderFilesHelper
import pandas as pd

from subsurface.modules.reader.wells._read_to_df import check_format_and_read_to_df


def read_collar(reader_helper: GenericReaderFilesHelper) -> pd.DataFrame:
    if reader_helper.usecols is None: reader_helper.usecols = [0, 1, 2, 3]
    if reader_helper.index_col is False: reader_helper.index_col = 0

    # Check file_or_buffer type
    d = check_format_and_read_to_df(reader_helper)
    _map_rows_and_cols_inplace(d, reader_helper)

    return d


def read_survey(reader_helper: GenericReaderFilesHelper):
    if reader_helper.index_col is False: reader_helper.index_col = 0

    d = check_format_and_read_to_df(reader_helper)
    _map_rows_and_cols_inplace(d, reader_helper)

    d_no_singles = _validate_survey_data(d)

    return d_no_singles


def _map_rows_and_cols_inplace(d: pd.DataFrame, reader_helper: GenericReaderFilesHelper):
    if reader_helper.index_map is not None:
        d.rename(reader_helper.index_map, axis="index", inplace=True)  # d.index = d.index.map(reader_helper.index_map)
    if reader_helper.columns_map is not None:
        d.rename(reader_helper.columns_map, axis="columns", inplace=True)
        # d.columns = d.columns.map(reader_helper.columns_map)


def _validate_survey_data(d):
    if not d.columns.isin(['md']).any():
        raise AttributeError(
            'md, inc, and azi columns must be present in the file. Use columns_map to assign column names to these fields.')

    elif not np.isin(['md', 'inc', 'azi'], d.columns).all():
        warnings.warn(
            'inc and/or azi columns are not present in the file. The boreholes will be straight.')
        
        d['inc'] = 0
        d['azi'] = 0

    # Drop wells that contain only one value
    d_no_singles = d[d.index.duplicated(keep=False)]
    return d_no_singles
