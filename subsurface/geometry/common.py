

class Common(object):
    """A set of shared functionality for all spatially referenced data."""

    def validate(self):
        raise NotImplementedError()

    def to_pyvista(self):
        raise NotImplementedError()
