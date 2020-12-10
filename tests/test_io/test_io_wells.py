from subsurface import PointSet
from subsurface.io import borehole_location_to_unstruct
from subsurface.visualization import to_pyvista_points, pv_plot
import pandas as pd


def test_borehole_location_to_unstruct(data_path):
    us = borehole_location_to_unstruct(
        data_path+'/borehole/borehole_collar.xlsx', {})
    point_set = PointSet(us)
    s = to_pyvista_points(point_set)
    #pv_plot([s], image_2d=True)


def test_generate_tops(data_path):
    d = pd.read_csv(data_path+'/borehole/no_tops.csv')
    d['_'] = d['Z'] - d['Altitude']
    Z_shift = d.groupby('Index')['_'].shift(1)
    Z_0 = Z_shift.fillna(0)
    v = Z_0 + d['Altitude']
    # diff = v.groupby('Index').Z.diff()
    # diff_0 = diff.fillna(0) + d['Altitude']
    # print(diff_0)
    print(v)
    d['top'] = v
    print(d)



