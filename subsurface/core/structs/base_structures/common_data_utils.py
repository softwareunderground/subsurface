import os
import warnings
from typing import Union

from .structured_data import StructuredData
from .unstructured_data import UnstructuredData


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


def to_netcdf(base_data: Union[StructuredData, UnstructuredData], path=None, file: str = None, **kwargs):
    if path is None and file is not None:
        # TODO: Mark file as deprecated
        warnings.warn("file argument is deprecated, please use path instead", DeprecationWarning)
        name, path = default_path_and_name(path, file)
    return base_data.data.to_netcdf(path, format="NETCDF4", **kwargs)


def default_path_and_name(path, name='subsurface_data.nc', ):
    if not path:
        path = './'
    if os.path.isdir(path):
        print("Directory already exists, files will be overwritten")
    else:
        os.makedirs(f'{path}')
    path = f'{path}/{name}'
    return name, path
