Interfaces
==========

Functionality to transform the *Subsurface data structures* to specific formats
other libraries of the subsurface stack understand.

In principle, this subpackage only is used for transformations that feed to more
than one library. Otherwise, **each individual library** should take care of the
transformation.

Notice, these modules are meant to be within the python ecosystem. To interact
with the exterior use the subpackage `io`.
