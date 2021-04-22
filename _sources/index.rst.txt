.. _subsurface-manual:

########################
subsurface Documentation
########################

:Release: |version|
:Date: |today|
:Source: `github.com/softwareunderground/subsurface <https://github.com/softwareunderground/subsurface>`_

----


.. include:: ../../README.rst
  :start-after: sphinx-inclusion-marker


Requirements
------------

The **only** requirement for ``subsurface`` is ``xarray`` (which, in turn,
requires ``pandas`` and ``numpy``).


Optional requirements
---------------------

There are many optional requirements, depending on the data format you want to
read/write. Currently, the ``requierements_opt.txt`` reads like:

.. include:: ../../requirements_opt.txt
   :literal:


.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: User Guide

   manual
   changelog
   contributing
   maintenance

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: Galleries

   examples/index
   external/external_examples

.. toctree::
   :maxdepth: 2
   :hidden:
   :caption: API Reference

   code-geological-formats
   code-interfaces
   code-reader
   code-structs
   code-utils
   code-viz
   code-writer
