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
