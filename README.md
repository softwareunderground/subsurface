# subsurface

DataHub for geoscientific data in Python. Two main purposes:

+ Unify geometric data into data objects (using numpy arrays as memory representation) that all the packages of the stack understand

+ Basic interactions with those data objects:
    + Write/Read
    + Categorized/Meta data
    + Visualization

## Data Levels:

**Human**

    geological_format -> Additional context/meta information about the data: OMF, geoh5py

    +-----------+

    geological_object -> Elements that represent some geological concept. E.g: faults, seismic

    +-----------+

    +-----------+

    element -> type of geometric object: PointSet, TriSurf, LineSet, Tetramesh

    +-----------+

    primary_structures -> Set of arrays that define a geometric object: StructuredData, UnstructuredData

    +-----------+

    +-----------+

    Dataframe/Xarray -> Label numpy.arrays

    +-----------+

    numpy.array -> Memory allocation

**Computer**

## Installation

The project is in pre-alpha and is not yet ready to be used.


#### Update 13.06.2020

We are changing things. Help us figure it out!

#### Original statement

The goal of this project is to support other subsurface geoscience and 
engineering projects with a set of classes for common subsurface data entities, 
such as seismic and GPR datasets, log curves, and so on. The current plan is to 
 use `xarray` under the hood, with `pint` for units support and `cartopy` for CRS and map support.

It's early days, everything might change. Help us figure it out!


