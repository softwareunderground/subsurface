import pytest
from conftest import RequirementsLevel

from subsurface import PointSet
from subsurface.reader.readers_data import ReaderFilesHelper
from subsurface.reader.wells import borehole_location_to_unstruct
from subsurface.visualization import to_pyvista_points, pv_plot
import pandas as pd


@pytest.mark.skipif(
    condition=(RequirementsLevel.WELLS | RequirementsLevel.BASE) not in RequirementsLevel.REQUIREMENT_LEVEL_TO_TEST(),
    reason="Need to set the READ_WELL variable to run this test"
)
def test_borehole_location_to_unstruct(data_path):
    us = borehole_location_to_unstruct(
        ReaderFilesHelper(
            file_or_buffer=data_path + '/borehole/borehole_collar.xlsx',
            header=None,
            columns_map={1: 'x', 2: 'y', 3: 'altitude'}
        )
    )
    point_set = PointSet(us)
    s = to_pyvista_points(point_set)


@pytest.mark.skipif(
    condition=RequirementsLevel.WELLS not in RequirementsLevel.REQUIREMENT_LEVEL_TO_TEST(),
    reason="Need to set the READ_WELL variable to run this test"
)
def test_generate_tops(data_path):
    d = pd.read_csv(data_path + '/borehole/no_tops.csv')
    d['_'] = d['Z'] - d['Altitude']
    Z_shift = d.groupby('Index')['_'].shift(1)
    Z_0 = Z_shift.fillna(0)
    v = Z_0 + d['Altitude']

    d['top'] = v
