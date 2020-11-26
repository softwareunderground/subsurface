"""
E1
==
Modify after @Alex Juistel
"""

# %%
import pathlib

import imageio
import pandas as pd
import numpy as np
import subsurface
from subsurface.io import LineSet
from subsurface.io.profiles import create_mesh_from_trace, \
    create_tri_surf_from_traces_texture, line_set_from_trace
from subsurface.io.wells import read_wells_to_unstruct, borehole_location_to_unstruct
import os

# %%
data_path = os.path.abspath(
    os.path.dirname(__file__) + '../../../data/Daten_Miguel/')

well_adding_md = pd.read_csv(data_path + '/wells.csv')
well_adding_md['md'] = well_adding_md['Altitude'] - well_adding_md['Z']
well_adding_md.to_csv(data_path + '/wells_fix.csv')


# %%

def wells_to_mesh():
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
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element, radius=50)
    # Plot default LITH
    # subsurface.visualization.pv_plot([pyvista_mesh], image_2d=False)
    return pyvista_mesh


# %%
def collars_to_mesh():
    borehole_location_struct = borehole_location_to_unstruct(
        collar_file=data_path + '/wells.csv',
        read_collar_kwargs={
            'usecols': ['Index', 'X', 'Y', 'Altitude'],
            'header': 0
        }
    )

    point_set = subsurface.structs.PointSet(borehole_location_struct)
    s = subsurface.visualization.to_pyvista_points(point_set)
    return s


def topo_to_mesh():
    topo = subsurface.io.read_structured_topography(data_path + '/DEM25.tif')
    topo.replace_outliers('topography', 0.98)
    topo_sg = subsurface.structs.StructuredGrid(topo)
    topo_mesh = subsurface.visualization.to_pyvista_grid(topo_sg, 'topography')
    return topo_mesh


def plot_meshes(list):
    subsurface.visualization.pv_plot(
        list,
        image_2d=False,
        ve=5
    )

#
# mesh_list = create_tri_surf_from_traces_texture(
#     data_path + '/profiles/Traces.shp',
#     path_to_texture=[
#         data_path + '/profiles/Profil1_cropped.png',
#         data_path + '/profiles/Profil2_cropped.png',
#         data_path + '/profiles/Profil3_cropped.png',
#         data_path + '/profiles/Profil4_cropped.png',
#         data_path + '/profiles/Profil5_cropped.png',
#         data_path + '/profiles/Profil6_cropped.png',
#         data_path + '/profiles/Profil7_cropped.png',
#     ]
# )

mesh_list2 = create_tri_surf_from_traces_texture(
    data_path + '/Profiles_cropped/Profile_PyVista.shp',
    path_to_texture=[
        data_path + '/Profiles_cropped/profile001_Gronau_GK100.png',
        data_path + '/Profiles_cropped/profile002_Muenster_GK200.png',
        data_path + '/Profiles_cropped/profile003_Lingen_GK200.png',
        data_path + '/Profiles_cropped/profile004_Bielefeld_GK200.png',
        data_path + '/Profiles_cropped/profile005_Duesseldorf_GK200.png',
        data_path + '/Profiles_cropped/profile006_Muenster_GK100.png',
        data_path + '/Profiles_cropped/profile007_Rheine_GK100.png',
        data_path + '/Profiles_cropped/profile008_Rheine2_GK100.png',
        data_path + '/Profiles_cropped/profile009_Bielefeld_GK100.png',
        data_path + '/Profiles_cropped/profile010_Recklinghausen1_GK100.png',
        data_path + '/Profiles_cropped/profile011_Recklinghausen2_GK100.png',
        data_path + '/Profiles_cropped/profile012_Guetersloh_GK100.png',
        data_path + '/Profiles_cropped/profile013_Guetersloh2_GK100.png',
    ],
    idx=range(13)
)

#traces = line_set_from_trace(data_path + '/profiles/Traces.shp')
traces2 = line_set_from_trace(
    data_path + '/Profiles_cropped/Profile_PyVista.shp',
    idx=range(13)
)
w = wells_to_mesh()
t = topo_to_mesh()
c = collars_to_mesh()

plot_meshes([#*mesh_list, *traces,
             *mesh_list2, *traces2,
             t, c,
             w
             ])
