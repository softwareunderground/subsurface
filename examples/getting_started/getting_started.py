"""
Getting started
===============
"""

# %%md
# Authors: Miguel de la Varga and Alexander Juestel
#
# This example how to read into subsurface structures a bunch of different
# data such as:
#
# - well data -> from csv all in one single file
#
# - topography -> from tif
#
# - Cross sections with textures from trace -> shp, png
#
# - Exported gempy model from netcdf


# %%
import shutil
import pandas as pd
import subsurface as ss
import pooch

# %%
# Read wells:
# -----------
# We can read well data - using welly as backend. First we need to have the
# data in the right format for digesting.

# %%

# Pulling data example
model_file = pooch.retrieve(
    url="https://github.com/cgre-aachen/gempy_data/raw/master/"
        "data/subsurface/example1.zip",
    known_hash=None
)

data_path = model_file[:-4]
shutil.unpack_archive(model_file, extract_dir=model_file[:-4])

# Read original file
ori_wells = pd.read_csv(data_path + '/wells.csv')

# Add top and base columns
wells_fixed = ss.io.wells.add_tops_from_base_and_altitude_in_place(
    ori_wells,
    'Index',
    'Z',
    'Altitude'
)

wells_fixed['md'] = wells_fixed['top']
wells_fixed.to_csv(data_path + '/wells.csv')
wells_fixed

# %%md
# Now we can read the csv files into subsurface.UnstructuredData

# %%
wells_unstructured_data = ss.io.read_wells_to_unstruct(
    collar_file=data_path + '/wells.csv',
    read_collar_kwargs={
        'usecols': ['Index', 'X', 'Y', 'Altitude'],
        'header': 0
    },
    survey_file=data_path + '/wells.csv',
    read_survey_kwargs={
        'index_col': 'Index',
        'usecols': ['Index', 'md']  # if incl and azi not given -> well vertical
    },
    lith_file=data_path + '/wells.csv',
    read_lith_kwargs={
        'index_col': 'Index',
        'usecols': ['Index', 'top', 'base', 'formation'],
        'columns_map': {'top': 'top',
                        'base': 'base',
                        'formation': 'component lith',
                        }
    }

)


# %%
wells_unstructured_data

# %%md
# From UnstructuredData we can create geometric objects such a lines, points, meshes,
# etc. In the case of boreholes `subsurface.LineSet` is the most suitable geometric
# representation.

# %%
wells_element = ss.LineSet(wells_unstructured_data)

# %%
# All elements in subsurface have their direct link to a pyvista mesh. This
# transformation can be done by the functions `to_pyvista_...`.

# Pyvista mesh
wells_mesh = ss.visualization.to_pyvista_line(wells_element, radius=50)

# Plotting
ss.visualization.pv_plot(
    [wells_mesh],
    image_2d=False,
    ve=5
)

# %%md
# We can do the same for point data, for example the borehole location.

# %%

# UnstructuredData
borehole_location_struct = ss.io.borehole_location_to_unstruct(
    collar_file=data_path + '/wells.csv',
    read_collar_kwargs={
        'usecols': ['Index', 'X', 'Y', 'Altitude'],
        'header': 0
    }
)
borehole_location_struct

# %%
# Element
borehole_location_point_set = ss.PointSet(borehole_location_struct)
borehole_location_point_set

# %%
# Pyvista mesh
borehole_loc_mesh = ss.visualization.to_pyvista_points(borehole_location_point_set)
borehole_loc_mesh

# %%
ss.visualization.pv_plot(
    [borehole_loc_mesh],
    image_2d=False,
    ve=5
)


# %%md
# Read Topography
# ---------------

# %%

# StructuredData
topo_structured_data = ss.io.read_structured_topography(data_path + '/DEM50.tif')
topo_structured_data
# %%
# Remove outliers
topo_structured_data.replace_outliers('topography', 0.98)

# Element
topo_element = ss.structs.StructuredGrid(topo_structured_data)
topo_element

# Pyvista mesh
topo_mesh = ss.visualization.to_pyvista_grid(topo_element, 'topography',
                                             data_order='C')

# %%
ss.visualization.pv_plot(
    [topo_mesh],
    image_2d=False,
    ve=5
)

