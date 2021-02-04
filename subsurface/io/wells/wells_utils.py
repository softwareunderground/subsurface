import pandas as pd


def add_tops_from_base_and_altitude_in_place(
        data: pd.DataFrame,
        col_well_name: str,
        col_base: str,
        col_altitude: str) -> pd.DataFrame:
    d = data
    repeated_rows = mark_repeated_rows(d['base'])
    d = d[~repeated_rows] # removed repeated rows
    d.loc[:, 'base'] = d[col_altitude] - d[col_base]
    Z_shift = d.groupby(col_well_name)['base'].shift(1)
    Z_0 = Z_shift.fillna(0)
    v = Z_0 + d[col_altitude]
    d.loc[:, 'top'] = Z_0
    d.loc[:, '_top_abs'] = v
    if "md" not in d.columns:
        d.loc[:, 'md'] = d['top']
    return d


def mark_repeated_rows(series: pd.Series):
    return series.shift(1) == series