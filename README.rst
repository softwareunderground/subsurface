.. image:: https://raw.githubusercontent.com/softwareunderground/subsurface/main/docs/source/_static/logos/subsurface.png
   :target: https://softwareunderground.github.io/subsurface
   :alt: subsurface logo

|

.. image:: https://img.shields.io/pypi/v/subsurface.svg
   :target: https://pypi.python.org/pypi/subsurface/
   :alt: PyPI
.. image:: https://img.shields.io/conda/v/conda-forge/subsurface.svg
   :target: https://anaconda.org/conda-forge/subsurface/
   :alt: conda-forge
.. image:: https://img.shields.io/badge/python-3.8+-blue.svg
   :target: https://www.python.org/downloads/
   :alt: Supported Python Versions
.. image:: https://img.shields.io/badge/platform-linux,win,osx-blue.svg
   :target: https://anaconda.org/conda-forge/emg3d/
   :alt: Linux, Windows, OSX
.. image:: https://img.shields.io/badge/slack-swung-1DB6ED.svg?logo=slack
   :target: http://swu.ng/slack
   :alt: SWUNG Slack

|


.. sphinx-inclusion-marker


subsurface
==========


DataHub for geoscientific data in Python. Two main purposes:

+ Unify geometric data into data objects (using numpy arrays as memory representation) that all the packages of the stack understand

+ Basic interactions with those data objects:
    + Write/Read
    + Categorized/Meta data
    + Visualization


Data Levels
-----------

The difference between data levels is **not** which data they store but which data they **parse and understand**. The rationale for this is to be able to pass along any object while keeping the I/O in subsurface::

                HUMAN

   \‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾/\
    \= = = = = = = = = = = = = = /. \     -> Additional context/meta information about the data
     \= = = = geo_format= = = = /. . \
      \= = = = = = = = = = = = /. . . \   -> Elements that represent some
       \= = = geo_object= = = /. . . . \     geological concept. E.g: faults, seismic
        \= = = = = = = = = = /. . . . ./
         \= = element = = = /. . . . /    -> type of geometric object: PointSet,
          \= = = = = = = = /. . . ./         TriSurf, LineSet, Tetramesh
           \primary_struct/. . . /        -> Set of arrays that define a geometric object:
            \= = = = = = /. . ./             e.g. *StructuredData*, *UnstructuredData*
             \DF/Xarray /. . /            -> Label numpy.arrays
              \= = = = /. ./
               \array /. /                -> Memory allocation
                \= = /./
                 \= //
                  \/

               COMPUTER


Documentation (WIP)
-------------------

Note that ``subsurface`` is still in early days; do expect things to change. We
welcome contributions very much, please get in touch if you would like to add
support for subsurface in your package.

An early version of the documentation can be found here:

https://softwareunderground.github.io/subsurface/

Direct links:

- `Developers-guide <https://softwareunderground.github.io/subsurface/maintenance.html>`_
- `Changelog <https://softwareunderground.github.io/subsurface/changelog.html>`_


Installation
------------

.. code-block:: console

    pip install subsurface

or

.. code-block:: console

    conda install -c conda-forge subsurface

Be aware that to read different formats you will need to manually install the
specific dependency (e.g. ``welly`` to read well data).

