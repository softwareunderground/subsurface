"""
E1
==

"""

# %%
import pathlib
import pandas as pd
import subsurface
from subsurface.io import LineSet
from subsurface.io.wells import read_wells_to_unstruct, borehole_location_to_unstruct
import os

# %%
data_path = os.path.abspath(
    os.path.dirname(__file__) + '../../../data/Daten_Miguel/')

well_adding_md = pd.read_csv(data_path + '/wells.csv')
well_adding_md['md'] = well_adding_md['Altitude'] - well_adding_md['Z']
well_adding_md.to_csv(data_path + '/wells_fix.csv')


# %%

def read_wells():
    us = read_wells_to_unstruct(
        collar_file=data_path + '/wells_fix.csv',
        read_collar_kwargs={
            'usecols': ['Index', 'X', 'Y', 'Altitude'],
            'header': 0
        },
        survey_file=data_path + '/wells_fix.csv',
        read_survey_kwargs={
            'index_col': 'Index',
           # 'columns_map': {'Z': 'md'}
        }

    )

    # %%
    element = LineSet(us)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element, radius=10)
    # Plot default LITH
    # subsurface.visualization.pv_plot([pyvista_mesh], image_2d=False)
    return pyvista_mesh


# wells_mesh = read_wells()

borehole_location_struct = borehole_location_to_unstruct(
    collar_file=data_path + '/wells.csv',
    read_collar_kwargs={
        'usecols': ['Index', 'X', 'Y', 'Altitude'],
        'header': 0
    }
)

point_set = subsurface.structs.PointSet(borehole_location_struct)
s = subsurface.visualization.to_pyvista_points(point_set)

topo = subsurface.io.read_structured_topography(data_path + '/DEM25.tif')
topo.replace_outliers('topography', 0.98)
topo_sg = subsurface.structs.StructuredGrid(topo)
topo_mesh = subsurface.visualization.to_pyvista_grid(topo_sg, 'topography')

subsurface.visualization.pv_plot(
    [s,  topo_mesh],
    image_2d=False,
    ve=8
)
