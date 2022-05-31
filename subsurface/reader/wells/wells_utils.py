from typing import List

import pandas as pd
import numpy as np


__all__ = ['add_tops_from_base_and_altitude_in_place',
           'fix_wells_higher_base_than_top_inplace', 'map_attr_to_segments',
           'pivot_wells_df_into_segment_per_row']

def add_tops_from_base_and_altitude_in_place(data: pd.DataFrame, col_well_name: str, col_base: str,
                                             col_altitude: str) -> pd.DataFrame:
    d = data
    d = _remove_repeated_rows(d)
    #_create_base_col(col_altitude, col_base, d)
    _create_top_col(col_altitude, col_well_name, d)
    _add_md_col_if_missing(d)
    return d

def xyz_coordinates_to_md_azimuth_inclination(self, xyz_array) -> np.ndarray:
    """
    Converts a numpy array of xyz coordinates to md, azimuth, dip in degrees
    """
    # # ! So far we are assuming the coordinates are absolute (instead to be relative to the datum)

    xyz_array = np.array(xyz_array)

    # Shift xyz_array to origin
    xyz_array_origin = xyz_array - xyz_array[0]

    # Get md
    md = np.linalg.norm(xyz_array_origin, axis=1)

    # Get azimuth and dip
    azimuth = np.arctan2(xyz_array_origin[:, 0], xyz_array_origin[:, 1])
    dip = np.arctan2(xyz_array_origin[:, 2], np.sqrt(xyz_array_origin[:, 0] ** 2 + xyz_array_origin[:, 1] ** 2))

    # Convert to degrees
    azimuth = np.rad2deg(azimuth)
    dip = np.rad2deg(dip)

    # Make sure azimuth is between 0 and 360
    azimuth[azimuth < 0] = azimuth[azimuth < 0] + 360

    dip = + 90 + dip

    return np.vstack((md, azimuth, dip)).T


def fix_wells_higher_base_than_top_inplace(df_fixed) -> pd.DataFrame:
    top_base_error = df_fixed["top"] > df_fixed["base"]
    df_fixed["base"][top_base_error] = df_fixed["top"] + 0.01
    return df_fixed


def map_attr_to_segments(df, attr_per_segment: List, n_wells: int) -> pd.DataFrame:
    tiled_formations = pd.np.tile(attr_per_segment, (n_wells))
    df['formation'] = tiled_formations
    return df


def pivot_wells_df_into_segment_per_row(df: pd.DataFrame, start_segment_cols: int, n_segments_per_well: int) -> pd.DataFrame:
    # Repeat fixed rows (collar name and so)
    df_fixed = df.iloc[:, :start_segment_cols]
    df_fixed = df_fixed.loc[df_fixed.index.repeat(n_segments_per_well)]

    df_bottoms = df.iloc[:, start_segment_cols:start_segment_cols + n_segments_per_well]
    df_fixed['base'] = df_bottoms.values.reshape(-1, 1, order='C')

    return df_fixed


def _add_md_col_if_missing(d):
    if "md" not in d.columns:
        d.loc[:, 'md'] = d['top']


def _create_top_col(col_altitude, col_well_name, d):
    Z_shift = d.groupby(col_well_name)['base'].shift(1)
    Z_0 = Z_shift.fillna(Z_shift[1])
    v = Z_0 + d[col_altitude]
    d.loc[:, 'top'] = Z_0
    d.loc[:, '_top_abs'] = v


def _create_base_col(col_altitude, col_base, d):
    d.loc[:, 'base'] = d[col_altitude] - d[col_base]


def _remove_repeated_rows(d):
    repeated_rows = _mark_repeated_rows(d['base'])
    d = d[~repeated_rows]  # removed repeated rows
    return d


def _mark_repeated_rows(series: pd.Series):
    return series.shift(1) == series
