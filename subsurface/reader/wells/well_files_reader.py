import io
import pathlib
import warnings
from typing import Optional, Union, List

import pandas as pd

from subsurface.reader.wells.wells_utils import add_tops_from_base_and_altitude_in_place


def _dict_reader(dict_):
    """

    Args:
        dict_: data, index, columns

    """
    return pd.DataFrame(data=dict_['data'],
                        columns=dict_['columns'],
                        index=dict_['index'])


def _get_reader(file_format):
    if file_format == '.xlsx':
        reader = pd.read_excel
    elif file_format == 'dict':
        reader = _dict_reader
    else:
        reader = pd.read_csv
    return reader


def read_collar(file_or_buffer, **kwargs) -> pd.DataFrame:
    """

    Args:
        file_or_buffer:
        **kwargs:
            usecols: well_name, X, Y, Z

    Returns:

    """

    header = kwargs.pop('header', None)
    cols = kwargs.pop('usecols', [0, 1, 2, 3])
    index_col = kwargs.pop('index_col', 0)
    is_json = kwargs.pop('is_json', False)
    index_map = kwargs.pop('index_map', None)
    columns_map = kwargs.pop('columns_map', None)

    # Check file_or_buffer type
    if is_json is True:
        d = pd.read_json(file_or_buffer, orient='split')

    elif type(file_or_buffer) == str or isinstance(file_or_buffer, pathlib.PurePath):
        file_or_buffer = pathlib.Path(file_or_buffer)
        file_format = file_or_buffer.suffix
        reader = _get_reader(file_format)
        d = reader(file_or_buffer,
                   usecols=cols,
                   header=header,
                   index_col=index_col, **kwargs)

    elif type(file_or_buffer) == io.BytesIO or \
            type(file_or_buffer) == io.StringIO:
        reader = _get_reader('.csv')
        d = reader(file_or_buffer,
                   usecols=cols,
                   header=header,
                   index_col=index_col, **kwargs)

    elif type(file_or_buffer) == dict:
        reader = _get_reader('dict')
        d = reader(file_or_buffer)

    else:
        raise AttributeError('file_or_buffer must be either a path or a dict')

    if index_map is not None:
        d.index = d.index.map(index_map)

    if columns_map is not None:
        d.columns = d.columns.map(columns_map)

    return d


def read_survey(file_or_buffer, index_map=None, columns_map=None, **kwargs):
    is_json = kwargs.pop('is_json', False)
    index_col = kwargs.pop('index_col', 0)

    if is_json is True:
        d = pd.read_json(file_or_buffer, orient='split')

    elif type(file_or_buffer) == str or isinstance(file_or_buffer, pathlib.PurePath):

        file_or_buffer = pathlib.Path(file_or_buffer)
        file_format = file_or_buffer.suffix
        reader = _get_reader(file_format)
        d = reader(file_or_buffer, index_col=index_col, **kwargs)

    elif type(file_or_buffer) == io.BytesIO or \
            type(file_or_buffer) == io.StringIO:
        reader = _get_reader('.csv')
        d = reader(file_or_buffer, index_col=index_col, **kwargs)

    elif type(file_or_buffer) == dict:
        reader = _get_reader('dict')
        d = reader(file_or_buffer)
    else:
        raise AttributeError('file_or_buffer must be either a path or a dict')

    if index_map is not None:
        d.index = d.index.map(index_map)

    if columns_map is not None:
        d.columns = d.columns.map(columns_map)

    if not d.columns.isin(['md']).any():
        raise AttributeError('md, inc, and azi columns must be present in the file.'
                             'Use columns_map to assign column names to these fields.')

    elif not pd.np.isin(['md', 'inc', 'azi'], d.columns).all():
        warnings.warn('inc and/or azi columns are not present in the file.'
                      ' The boreholes will be straight.')
        d['inc'] = 0
        d['azi'] = 0

    # Drop wells that contain only one value
    d_no_singles = d[d.index.duplicated(keep=False)]

    return d_no_singles


def read_lith(file_or_buffer, columns_map=None, **kwargs):
    """Columns MUST contain:
        - top
        - base
        - component lith
    """
    is_json = kwargs.pop('is_json', False)
    index_col = kwargs.pop('index_col', 0)

    if is_json is True:
        d = pd.read_json(file_or_buffer, orient='split')

    elif type(file_or_buffer) == str or isinstance(file_or_buffer, pathlib.PurePath):
        file_or_buffer = pathlib.Path(file_or_buffer)
        file_format = file_or_buffer.suffix
        reader = _get_reader(file_format)
        d = reader(file_or_buffer, index_col=index_col, **kwargs)
    elif type(file_or_buffer) == io.BytesIO or \
            type(file_or_buffer) == io.StringIO:

        reader = _get_reader('.csv')
        d = reader(file_or_buffer, index_col=index_col, **kwargs)
    elif type(file_or_buffer) == dict:

        reader = _get_reader('dict')
        d = reader(file_or_buffer)
    else:
        raise AttributeError('file_or_buffer must be either a path or a dict')

    if columns_map is not None:
        d.columns = d.columns.map(columns_map)

    given_top = pd.np.isin(['top', 'base', 'component lith'], d.columns).all()
    given_altitude_and_base = pd.np.isin(
        ['altitude', 'base', 'component lith'], d.columns).all()

    if given_altitude_and_base and not given_top:
        d = add_tops_from_base_and_altitude_in_place(
            d,
            index_col,
            'base',
            'altitude'
        )

    elif not given_top and not given_altitude_and_base:
        raise ValueError('basis column must be present in the file. Use '
                         'columns_map to assign column names to these fields.')
    return d[['top', 'base', 'component lith']]


def read_attributes(file_or_buffer, columns_map=None,
                    drop_cols: Optional[list] = None, **kwargs):
    is_json = kwargs.pop('is_json', False)
    if is_json is True:
        d = pd.read_json(file_or_buffer, orient='split')
    elif type(file_or_buffer) == str or isinstance(file_or_buffer, pathlib.PurePath):
        file_or_buffer = pathlib.Path(file_or_buffer)
        file_format = file_or_buffer.suffix
        reader = _get_reader(file_format)
        index_col = kwargs.pop('index_col', 0)
        d = reader(file_or_buffer, index_col=index_col, **kwargs)

    elif type(file_or_buffer) == io.BytesIO or \
            type(file_or_buffer) == io.StringIO:

        reader = _get_reader('.csv')
        index_col = kwargs.pop('index_col', 0)
        d = reader(file_or_buffer, index_col=index_col, **kwargs)

    elif type(file_or_buffer) == dict:
        reader = _get_reader('dict')
        d = reader(file_or_buffer)
    else:
        raise AttributeError('file_or_buffer must be either a path or a dict')

    if columns_map is not None:
        d.rename(columns_map, axis=1, inplace=True)
    if drop_cols is not None:
        d.drop(drop_cols, axis=1, inplace=True)

    assert d.columns.isin(['basis']).any(), 'basis column' \
                                            'must be present in the file.' \
                                            'Use columns_map to assign' \
                                            'column names to these fields.'
    return d


def read_borehole_files(
        collar_file: str = None,
        survey_file: str = None,
        lith_file: str = None,
        attrib_file: Union[str, List] = None,
        read_collar_kwargs=None,
        read_survey_kwargs=None,
        read_lith_kwargs=None,
        read_attributes_kwargs=None,
):
    data_frames = dict()

    if read_attributes_kwargs is None:
        read_attributes_kwargs = {}
    if read_lith_kwargs is None:
        read_lith_kwargs = {}
    if read_survey_kwargs is None:
        read_survey_kwargs = {}
    if read_collar_kwargs is None:
        read_collar_kwargs = {}

    if collar_file is not None:
        collars = read_collar(collar_file, **read_collar_kwargs)
        data_frames['collar_df'] = collars

    if survey_file is not None:
        col_map = read_survey_kwargs.pop('columns_map', None)
        idx_map = read_survey_kwargs.pop('index_map', None)
        survey = read_survey(
            survey_file,
            index_map=idx_map,
            columns_map=col_map,
            **read_survey_kwargs)
        data_frames['survey_df'] = survey

    if lith_file is not None:
        col_map = read_lith_kwargs.pop('columns_map', None)
        lith = read_lith(lith_file, columns_map=col_map, **read_lith_kwargs)
        data_frames['lith_df'] = lith

    # First check if is just a path or list
    if attrib_file is not None:
        if type(attrib_file) is str:
            attrib_file = list(attrib_file)

        drop_cols = read_attributes_kwargs.pop('drop_cols',
                                               [None] * len(attrib_file))
        col_map = read_attributes_kwargs.pop('columns_map',
                                             [None] * len(attrib_file))

        attributes_ = list()
        for e, f in enumerate(attrib_file):
            attributes = read_attributes(
                f,
                drop_cols=drop_cols[e],
                columns_map=col_map[e],
                **read_attributes_kwargs
            )
            attributes_.append(attributes)

        data_frames['attrib_dfs'] = attributes_

    return data_frames
