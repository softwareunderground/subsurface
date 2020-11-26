from subsurface import PointSet
from subsurface.io import borehole_location_to_unstruct
from subsurface.visualization import to_pyvista_points, pv_plot


def test_borehole_location_to_unstruct(data_path):
    us = borehole_location_to_unstruct(
        data_path+'/borehole/borehole_collar.xlsx', {})
    point_set = PointSet(us)
    s = to_pyvista_points(point_set)
    pv_plot([s], image_2d=False)