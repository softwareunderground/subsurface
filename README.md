# subsurface

DataHub for geoscientific data in Python. Two main purposes:

+ Unify geometric data into data objects (using numpy arrays as memory representation) that all the packages of the stack understand

+ Basic interactions with those data objects:
    + Write/Read
    + Categorized/Meta data
    + Visualization

## Data Levels:
The difference between data levels is **not** which data they store but which data they **parse and understand**. The rationale for this is to be able to pass along any object while keeping the I/O in subsurface.

**Human**


      \‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾/\
       \= = = = = = = = = = = = = = /. \     -> Additional context/meta information about the data
        \= = = = geo_format= = = = /. . \
         \= = = = = = = = = = = = /. . . \   -> Elements that represent some
          \= = = geo_object= = = /. . . . \      geological concept. E.g: faults, seismic
           \= = = = = = = = = = /. . . . ./
            \= = element = = = /. . . . /    -> type of geometric object: PointSet,
             \= = = = = = = = /. . . ./         TriSurf, LineSet, Tetramesh
              \primary_struct/. . . /        -> Set of arrays that define a geometric object:
               \= = = = = = /. . ./             e.g. *StructuredData* **UnstructuredData**
                \DF/Xarray /. . /            -> Label numpy.arrays
                 \= = = = /. ./
                  \array /. /                -> Memory allocation
                   \= = /./
                    \= //
                     \/


**Computer**

## Documentation (WIP)

An early version of the documentation can be found here:

https://softwareunderground.github.io/subsurface/

## Installation

`pip install subsurface`

Be aware that to read different formats you will need to manually install the specific dependency (e.g. welly to read well data).

## Changes Log

#### Update 13.06.2020

We are changing things. Help us figure it out!

#### Original statement

The goal of this project is to support other subsurface geoscience and
engineering projects with a set of classes for common subsurface data entities,
such as seismic and GPR datasets, log curves, and so on. The current plan is to
 use `xarray` under the hood, with `pint` for units support and `cartopy` for CRS and map support.

It's early days, everything might change. Help us figure it out!


