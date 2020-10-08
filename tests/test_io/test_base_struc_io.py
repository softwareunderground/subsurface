import xarray as xr
import numpy as np


def test_write_unstruc(unstruc):
    a = xr.DataArray(unstruc.vertex, dims=['points', 'XYZ'])
    b = xr.DataArray(unstruc.edges, dims=['edges', 'node'])
    e = xr.DataArray(unstruc.attributes)
    c = xr.Dataset({'v': a, 'e': b, 'a': e})
    print(c)


# def test_xarray_unst():
#     ds = xr.Dataset()
#     ds["mesh2d"] = xr.DataArray(
#         data=0,
#         attrs={
#             "cf_role": "mesh_topology",
#             "long_name": "Topology data of 2D mesh",
#             "topology_dimension": 2,
#             "node_coordinates": "node_x node_y",
#             "face_node_connectivity": "face_nodes",
#         }
#     )
#     ds = ds.assign_coords(
#         node_x=xr.DataArray(
#             data=np.array([0.0, 10.0, 10.0, 0.0, 20.0, 20.0]).reshape(-1, 2),
#             dims=["node"],
#         )
#     )
#     print(ds)



