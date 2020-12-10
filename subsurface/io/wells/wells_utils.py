import pandas as pd


def add_tops_from_base_and_altitude_in_place(
        data: pd.DataFrame,
        col_well_name: str,
        col_base: str,
        col_altitude: str) -> pd.DataFrame:
    d = data
    d['base'] = d[col_altitude] - d[col_base]
    Z_shift = d.groupby(col_well_name)['base'].shift(1)
    Z_0 = Z_shift.fillna(0)
    v = Z_0 + d[col_altitude]
    d['top'] = Z_0
    d['_top_abs'] = v
    #d['base'] =
    return d