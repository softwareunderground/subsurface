"""
E1
==
authors: Miguel de la Varga and Alexander Juestel
"""

# %%md
# This example how to read into subsurface structuctures a bunch of differnt
# data such as:
# - well data -> from csv all in one single file
# - topography -> from tif
# - Cross sections with textures from trace -> shp, png
# - Exported gempy model from netcdf


# First we need to clean the borehole data:
# -----------------------------------------

# %%

import pandas as pd
import subsurface
from subsurface.interfaces import base_structs_to_binary_file
from subsurface.io import LineSet
from subsurface.io.profiles import create_tri_surf_from_traces_texture, \
    line_set_from_trace
from subsurface.io.wells import read_wells_to_unstruct, borehole_location_to_unstruct
from subsurface.io.wells.wells_utils import add_tops_from_base_and_altitude_in_place
import os

# %%

data_path = os.path.abspath(
    os.path.dirname(__file__) + '../../../data/data_example1/')

# Read original file
ori_wells = pd.read_csv(data_path + '/wells.csv')

# Add top and base columns
well_adding_tops = add_tops_from_base_and_altitude_in_place(
    ori_wells,
    'Index',
    'Z',
    'Altitude'
)

well_adding_md = well_adding_tops
well_adding_md['md'] = well_adding_md['top']
well_adding_md.to_csv(data_path + '/wells_fix.csv')

# %%

# Creat UnstructuredData
wells_us = read_wells_to_unstruct(
    collar_file=data_path + '/wells_fix.csv',
    read_collar_kwargs={
        'usecols': ['Index', 'X', 'Y', 'Altitude'],
        'header': 0
    },
    survey_file=data_path + '/wells_fix.csv',
    read_survey_kwargs={
        'index_col': 'Index',
        'usecols': ['Index', 'md']  # if incl and azi not given -> well vertical
    },
    lith_file=data_path + '/wells_fix.csv',
    read_lith_kwargs={
        'index_col': 'Index',
        'usecols': ['Index', 'top', 'base', 'formation'],
        'columns_map': {'top': 'top',
                        'base': 'base',
                        'formation': 'component lith',
                        }
    }

)
wells_us

# %%
# Create subsurface.element
element = LineSet(wells_us)

# Pyvista mesh
wells_mesh = subsurface.visualization.to_pyvista_line(element, radius=50)

# %%
# Create UnstructureData of the borehole location

# %%

# UnstructuredData
borehole_location_struct = borehole_location_to_unstruct(
    collar_file=data_path + '/wells.csv',
    read_collar_kwargs={
        'usecols': ['Index', 'X', 'Y', 'Altitude'],
        'header': 0
    }
)
borehole_location_struct

# %%
# Element
point_set = subsurface.structs.PointSet(borehole_location_struct)
point_set

# %%
# Pyvista mesh
borehole_loc_mesh = subsurface.visualization.to_pyvista_points(point_set)
borehole_loc_mesh

# %%

# StructuredData
topo = subsurface.io.read_structured_topography(data_path + '/DEM25.tif')
topo
# %%
# Remove outliers
topo.replace_outliers('topography', 0.98)

# Element
topo_sg = subsurface.structs.StructuredGrid(topo)
topo_sg

# Pyvista mesh
topo_mesh = subsurface.visualization.to_pyvista_grid(topo_sg, 'topography')

# %%
# Read Topography
# ---------------

# %%
trisurf_list, mesh_list = create_tri_surf_from_traces_texture(
    data_path + '/Profiles_cropped/Profile_PyVista.shp',
    path_to_texture=[
        data_path + '/Profiles_cropped/profile001.png',
        data_path + '/Profiles_cropped/profile002.png',
        data_path + '/Profiles_cropped/profile003.png',
        data_path + '/Profiles_cropped/profile004.png',
        data_path + '/Profiles_cropped/profile005.png',
        data_path + '/Profiles_cropped/profile006.png',
        data_path + '/Profiles_cropped/profile007.png',
        data_path + '/Profiles_cropped/profile008.png',
        data_path + '/Profiles_cropped/profile009.png',
        data_path + '/Profiles_cropped/profile010.png',
        data_path + '/Profiles_cropped/profile011.png',
        data_path + '/Profiles_cropped/profile012.png',
        data_path + '/Profiles_cropped/profile013.png',
    ],
    idx=range(13),
    return_mesh=True,
    return_uv=True
)

# %%
# UnstructuredData
gempy_us = subsurface.io.read_unstruct(data_path + '/meshes.nc')

# Element
trisurf_gempy = subsurface.TriSurf(gempy_us)

# Pyvista mesh
gempy_mesh = subsurface.visualization.to_pyvista_mesh(trisurf_gempy)

# %%

traces = line_set_from_trace(
    data_path + '/Profiles_cropped/Profile_PyVista.shp',
    idx=range(13)
)

#


meshes_list = ([*mesh_list, *traces, gempy_mesh,
                topo_mesh, borehole_loc_mesh, wells_mesh
                ])
# %%
# Plot mesh
subsurface.visualization.pv_plot(
    meshes_list,
    image_2d=False,
    ve=5
)


# %%
# Export to binary

# %%

base_structs_to_binary_file(data_path + '/le/gempy_base', gempy_us)
base_structs_to_binary_file(data_path + '/le/wells', wells_us)
base_structs_to_binary_file(data_path + '/le/topo', topo)
base_structs_to_binary_file(data_path + '/le/collars',
                            borehole_location_struct)

for e, tri_surf in enumerate(trisurf_list):
    base_structs_to_binary_file(data_path + f'/le/profile_{e}_mesh',
                                tri_surf.mesh)
    base_structs_to_binary_file(data_path + f'/le/profile_{e}_texture_C',
                                tri_surf.texture,
                                order='C')
