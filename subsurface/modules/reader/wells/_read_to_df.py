from subsurface.core.reader_helpers.readers_data import GenericReaderFilesHelper, SupportedFormats
import pandas as pd


def check_format_and_read_to_df(reader_helper: GenericReaderFilesHelper) -> pd.DataFrame:
    # ? This swithch is veeery confusing
    if reader_helper.format == ".json":
        d = pd.read_json(reader_helper.file_or_buffer, orient='split')
    elif reader_helper.is_file_in_disk:
        reader = _get_reader(reader_helper.format)
        d = reader(reader_helper.file_or_buffer, **reader_helper.pandas_reader_kwargs)
    elif reader_helper.is_bytes_string:
        reader = _get_reader('.csv')
        d = reader(reader_helper.file_or_buffer, **reader_helper.pandas_reader_kwargs)
    elif reader_helper.is_python_dict:
        reader = _get_reader('dict')
        d = reader(reader_helper.file_or_buffer)
    else:
        raise AttributeError('file_or_buffer must be either a path or a dict')

    if type(d.columns) is str:  d.columns = d.columns.str.strip()  # Remove spaces at the beginning and end
    if type(d.index) is str: d.index = d.index.str.strip()  # Remove spaces at the beginning and end
    return d


def _dict_reader(dict_):
    """

    Args:
        dict_: data, index, columns

    """
    return pd.DataFrame(
        data=dict_['data'],
        columns=dict_['columns'],
        index=dict_['index']
    )


def _get_reader(file_format):
    if file_format == SupportedFormats.XLXS:
        reader = pd.read_excel
    elif file_format == 'dict':
        reader = _dict_reader
    elif file_format == SupportedFormats.CSV:
        reader = pd.read_csv
    elif file_format == SupportedFormats.JSON:
        reader = _dict_reader
    else:
        raise ValueError(f"Subsurface is not able to read the following extension: {file_format}")
    return reader
