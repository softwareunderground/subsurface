import os
from typing import Union

from subsurface.structs.base_structures.structured_data import StructuredData
from subsurface.structs.base_structures.unstructured_data import UnstructuredData


__all__ = ['replace_outliers', 'to_netcdf', 'default_path_and_name']


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
        name, path = default_path_and_name(path, file)
    return base_data.data.to_netcdf(path, **kwargs)


def default_path_and_name(path, name='subsurface_data.nc', ):

    if not path:
        path = './'
    if os.path.isdir(path):
        print("Directory already exists, files will be overwritten")
    else:
        os.makedirs(f'{path}')
    path = f'{path}/{name}'
    return name, path
