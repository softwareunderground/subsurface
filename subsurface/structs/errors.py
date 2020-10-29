class PyVistaImportError(ImportError):
    message = """Trouble importing PyVista."""

    def __init__(self):
        """Empty init."""
        ImportError.__init__(self, self.message)


class VertexMissingError(Exception):
    message = """The columns have to be specified where surface_reader can expect vertices."""

    def __init__(self):
        """Empty init."""
        Exception.__init__(self, self.message)