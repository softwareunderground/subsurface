Maintenance
===========

Making a release
----------------

1. Add release notes to ``CHANGELOG.rst``.
2. Create a release on GitHub, add the above release notes to it.

When you create a release on GitHub it will run the tests, and subsequently
deploy the version to PyPI, from where it will also be picked up to
conda-forge. If everything works fine it should be available from PyPI within
minutes after the tests passed, and within an hour or two from conda-forge.


.. note::

   **Important.** Due to the use of ``setuptools_scm``, everything is by
   default added to the wheel on PyPI. Files and folders that should not be in
   a release have to be excluded by adding it to the ``MANIFEST.in``.


Type of commits
---------------

- ENH: Enhancement, new functionality
- BUG: Bug fix
- DOC: Additions/updates to documentation
- TST: Additions/updates to tests
- BLD: Updates to the build process/scripts
- PERF: Performance improvement
- CLN: Code cleanup
