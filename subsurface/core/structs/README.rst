Data Structures
===============

This subpackage intends to function as a wrapper for `pandas.Dataframe` and
`xarray`.

These are the ones which should be compatible between libraries - without the
attributes and metadata necessarily.

There are two levels of data structures:

- Base structures: Wrapper around xarray

- Elements: Composed of at least 1 base structured. Mirrors `pyvista` data structures

Base Structures
---------------

UnstructuredData
++++++++++++++++

`UnstructuredData` core data representation consist on a `xarray.Dataset` with the following data_vars:

- **Required**
    - "vertex": xr.DataArray(dims = ["points", "XYZ"])
    - "cell": xr.DataArray(dims=["cell", "nodes"])
    - default_vertex_attr_name: xr.DataArray(dims=["points", "points_attribute"])
    - default_cell_attr_name: xr.DataArray(dims=["cell", "cell_attribute"])

- **Optional**
    - Any other attr `xr.DataArray` as long as **at least** contain dim "cell" or "points"

 Note:

 default_vertex_attr_name and default_cell_attr_name can be given upon construction of the object. By default
 they are "cell_attr" and "vertex_attr".


StructuredData
++++++++++++++
- **Required**
    - data_array_name: xr.DataArray

- **Optional**
    - Any other `xr.DataArray` that share some dimension.

 Note:

 `data_array_name`  can be given upon construction of the object. By default
 it is "data_arra".


General Comments
----------------

- Readers, in general, they should aim to construct base structures with the required fields. Optional fields can be useful
  in certain situations but account for open data formats can increase the complexity of the overall project to unnecessary levels.