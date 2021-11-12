"""
Reading Simple GemPy model in Subsurface
========================================
"""

import sys

sys.path.insert(0, 'subsurface/')
import pooch
import subsurface as ss
import subsurface.reader.read_netcdf

# %% md
# Single surface
# --------------

# Pull gempy model
model_files = pooch.retrieve(
    url="https://github.com/cgre-aachen/gempy_data/raw/master/"
        "data/subsurface/example1.zip",
    known_hash="fb79a63eeb874cf0cdca557106c62c67eace23811db5935e57c3448fed7f8978",
    processor=pooch.Unzip()
)

# %%
fname, = [i for i in model_files if "meshes.nc" in i]
dataset = ss.reader.read_netcdf.read_unstruct(fname)

# %%
obj = ss.TriSurf(dataset)
print(obj.mesh.points_attributes_to_dict)

mesh = ss.visualization.to_pyvista_mesh(obj)
ss.visualization.pv_plot([mesh])


# %% md
# Four Layers
# -----------

# Pull gempy model
model_files_2 = pooch.retrieve(
    url="https://github.com/cgre-aachen/gempy_data/raw/master/data/gempy_models/Kim.zip",
    known_hash="f530a88351ed0e38673c6937161c59a2f69df92202e14c1e5d5729ed5d72a323",
    processor=pooch.Unzip()
)

# %% md
# Triangular meshes
# +++++++++++++++++

# %%
fname, = [i for i in model_files_2 if "meshes.nc" in i]
gempy_tri_mesh_unstruct =  ss.reader.read_netcdf.read_unstruct(fname)
tri_surf = ss.TriSurf(gempy_tri_mesh_unstruct)
mesh = ss.visualization.to_pyvista_mesh(tri_surf)
ss.visualization.pv_plot([mesh])

# %% md
# Regular grid
# ++++++++++++

fname, = [i for i in model_files_2 if "regular_grid.nc" in i]
gempy_struct = ss.reader.read_netcdf.read_struct(fname)
regular_grid = ss.StructuredGrid(gempy_struct)

# %%
pyvista_mesh = ss.visualization.to_pyvista_grid(regular_grid,
                                                data_set_name='property_matrix',
                                                attribute_slice={'Properties': 'id'}
                                                )

ss.visualization.pv_plot([pyvista_mesh])




# %%

pyvista_mesh = ss.visualization.to_pyvista_grid(regular_grid,
                                                data_set_name='block_matrix',
                                                attribute_slice={'Properties': 'id',
                                                                 'Features': 'Default series'})

ss.visualization.pv_plot([pyvista_mesh])
