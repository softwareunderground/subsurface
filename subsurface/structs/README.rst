Data Structures
===============

This subpackage intends to function as a wrapper for `pandas.Dataframe` and
`xarray`.

These are the ones which should be compatible between libraries - without the
attributes and metadata necessarily.

There are two levels of data structures:
- Base structures: Wrapper around xarray
- Elements: Composed of at least 1 base structured. Mirrors `pyvista` data structures


