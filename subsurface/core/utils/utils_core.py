from typing import Union

from pathlib import Path

from subsurface import StructuredData, UnstructuredData


def get_extension(path):
    try:
        p = Path(path)
        return p.suffix
    except TypeError:
        return False


def replace_outliers(base_data: Union[StructuredData, UnstructuredData], dim=0, perc=0.99, replace_for=None):
    """@Edoardo Guerreiro https://stackoverflow.com/questions/60816533/
     is-there-a-built-in-function-in-xarray-to-remove-outliers-from-a-dataset"""

    data = base_data.data
    # calculate percentile
    threshold = data[dim].quantile(perc)

    # find outliers and replace them with max among remaining values
    mask = data[dim].where(abs(data[dim]) <= threshold)
    if replace_for == 'max':
        max_value = mask.max().values
        # .where replace outliers with nan
        mask = mask.fillna(max_value)
    elif replace_for == 'min':
        min_value = mask.min().values
        # .where replace outliers with nan
        mask = mask.fillna(min_value)

    print(mask)
    data[dim] = mask

    return data
