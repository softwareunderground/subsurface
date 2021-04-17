"""
Reading Simple GemPy model in Subsurface
=================================
"""

import sys

sys.path.insert(0, 'subsurface/')
import pooch
import subsurface as ss
import subsurface.reader.read_netcdf


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
