import numpy as np
import pandas as pd

from subsurface.io.wells.wells_reader import read_to_welly


def read_wells_to_unstruct(backend='welly', n_points=1000,
                           return_welly=False, **kwargs):
    """

    Args:
        backend:
        n_points:
        **kwargs:

    Returns:

    Examples:
        unstructured_data = read_wells_to_unstruct(
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
    if backend == 'welly':
        wts = read_to_welly(**kwargs)
        unstruct = wts.to_subsurface(n_points=n_points)
        s = (unstruct, wts.p) if return_welly is True else (unstruct)

    else:
        raise AttributeError('Only welly is available at the moment')

    return s