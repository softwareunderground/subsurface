NOTES
-----

TODO: Re-work and automate this. Steps that should be necessary:


**Important.** Due to the use of ``setuptools_scm``, everything is by default
added to the wheel on PyPI. Documents that should not be in a release have to
be excluded by adding it to the ``MANIFEST.in``.


Making a release
----------------

Create a release on GitHub. This will run the tests, and then automatically
deploy it to PyPI, from where conda-forge will pick it up as well.
If everything works fine it should be available from PyPI within minutes after
the tests passed, and within an hour or two from conda-forge.


### Type of commits:

- ENH: Enhancement, new functionality
- BUG: Bug fix
- DOC: Additions/updates to documentation
- TST: Additions/updates to tests
- BLD: Updates to the build process/scripts
- PERF: Performance improvement
- CLN: Code cleanup
