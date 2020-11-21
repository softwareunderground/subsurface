from typing import Union

from subsurface.structs.base_structures import UnstructuredData, StructuredData


class Common(object):
    """A set of shared functionality for all spatially referenced data."""
    mesh: Union[UnstructuredData, StructuredData]

    def validate(self):
        raise NotImplementedError()

    def to_pyvista(self):
        raise NotImplementedError()

