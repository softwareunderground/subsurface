class PyVistaImportError(ImportError):
    message = """Trouble importing PyVista."""

    def __init__(self):
        """Empty init."""
        ImportError.__init__(self, self.message)
