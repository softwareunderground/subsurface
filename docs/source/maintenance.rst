Maintenance
===========

.. todo::

    TODO



Making a release
----------------

- Adding release notes to CHANGELOG.rst.
- Create a release on GitHub (add the above release notes to it). This will run
  the tests, and then automatically deploy it to PyPI, from where conda-forge
  will pick it up as well. If everything works fine it should be available from
  PyPI within minutes after the tests passed, and within an hour or two from
  conda-forge.


Notes
-----

.. note::

   **Important.** Due to the use of ``setuptools_scm``, everything is by
   default added to the wheel on PyPI. Documents that should not be in a
   release have to be excluded by adding it to the ``MANIFEST.in``.


Type of commits
---------------

- ENH: Enhancement, new functionality
- BUG: Bug fix
- DOC: Additions/updates to documentation
- TST: Additions/updates to tests
- BLD: Updates to the build process/scripts
- PERF: Performance improvement
- CLN: Code cleanup
