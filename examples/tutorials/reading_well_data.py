"""
Reading Well Data into Subsurface
=================================
"""

# %%md
# Authors: Miguel de la Varga and Alexander Juestel

# This example will get into detail about how we are using `welly` and `striplog` to
# import borehole data.

# We start by using pooch to download the dataset into a temp file;

# %%
import pooch

from dataclasses import asdict
import matplotlib.pyplot as plt
from striplog import Component

import subsurface as sb
from subsurface.reader import ReaderFilesHelper
from subsurface.reader.wells import read_collar, read_survey, read_lith, WellyToSubsurfaceHelper, welly_to_subsurface
from subsurface.structs.base_structures.common_data_utils import to_netcdf

base_url = "https://raw.githubusercontent.com/softwareunderground/subsurface/main/tests/data/borehole/"

data_hash = "efa90898bb435daa15912ca6f3e08cd3285311923a36dbc697d2aafebbafa25f"
raw_borehole_data_csv = pooch.retrieve(url=base_url + 'kim_ready.csv',
                                       known_hash=data_hash)
# %% md
# This dataset consist on a csv file containing the following columns: x, y, name, num, z, year, 7,8,9, altitude, base,
# formation, top, _top_abs and md. This is a good example of how varied borehole data can be provided. We will
# need to be able to extract specific information to construct the `subsurface` object.

# To read csv we are using `pandas` but since `pandas.read_csv` has a lot of arguments, we have created some
# helper classes to facilitate the reading of the data for this specific context. These *Helpers* are just a python
# data class with a bit of funcitonality for setter and getter.

# Also since well data sometimes is given in multiple files - for collars, asseys and surveys - we will read those
# subset of the data into its own `pandas.Dataframe`. Let's start:

# %%

reading_collars = ReaderFilesHelper(
    file_or_buffer=raw_borehole_data_csv,  # Path to file
    index_col="name",  # Column used as index
    usecols=['x', 'y', 'altitude', "name"]  # Specific columns for collar
)

# We can see the fields from the class easily converting it to a dict
asdict(reading_collars)

# %% md
# The rest of fields of ReaderFilesHelper would be used for different .csv configurations. With a `ReaderFilesHelper`
# we can use it for specific functions to read the file into pandas:

# %%
collar = read_collar(reading_collars)
collar

# %% md
# We do the same for survey and lithologies:

# %%
survey = read_survey(
    ReaderFilesHelper(
        file_or_buffer=raw_borehole_data_csv,
        index_col="name",
        usecols=["name", "md"]
    )
)
survey

# %%
lith = read_lith(
    ReaderFilesHelper(
        file_or_buffer=raw_borehole_data_csv,
        usecols=['name', 'top', 'base', 'formation'],
        columns_map={'top': 'top',
                     'base': 'base',
                     'formation': 'component lith',
                     }
    )
)

lith

# %% md
# At this point we have all the necessary data in `pandas.Dataframe`. However, to construct a `subsurface.UnstructuredData`
# object we are going to need to convert the data to the usual scheme of: *vertex*, *cells*, *vertex_attr* and *cells_attr*.
# To do this we will use `welly` and `striplog`
#
# Welly is a family of classes to facilitate the loading, processing, and analysis of subsurface wells and well data,
# such as striplogs, formation tops, well log curves, and synthetic seismograms.
#
# The class WellyToSubsurfaceHelper contains the methods to create a welly project and export it to a subsurface data class.

# %%
wts = WellyToSubsurfaceHelper(collar_df=collar, survey_df=survey, lith_df=lith)

# %% md
# In the field p is stored a welly project
# (https://github.com/agile-geoscience/welly/blob/master/tutorial/04_Project.ipynb) and we can use it to explore
# and visualize properties of each well.

# %%
wts.p

# %%
stripLog = wts.p[0].data['lith']
stripLog

# %%
stripLog.plot()
plt.gcf()

# %% md
# Once we have the `WellyToSubsurfaceHelper` the function `welly_to_subsurface` will directly convert the objet to
# `subsurface.UnstructuredData` -- using the trajectory module of `welly`.

# %%
formations = ["topo", "etchegoin", "macoma", "chanac", "mclure",
              "santa_margarita", "fruitvale",
              "round_mountain", "olcese", "freeman_jewett", "vedder", "eocene",
              "cretaceous",
              "basement", "null"]

unstruct = welly_to_subsurface(
    wts,
    table=[Component({'lith': l}) for l in formations] # This is to keep the lithology ids constant across all the wells
)
unstruct

# %%
# We can save the data into a netcdf by simply calling
to_netcdf(unstruct, "wells_unstructured.nc")

# %% md
# We are done. Now the well data is a `subsurface.UnstructuredData` and can be used as usual.

# %%
element = sb.LineSet(unstruct)
pyvista_mesh = sb.visualization.to_pyvista_line(element, radius=50)

# Plot default LITH
interactive_plot =sb.visualization.pv_plot([pyvista_mesh])

