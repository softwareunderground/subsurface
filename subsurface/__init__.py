import subsurface.io
from subsurface.structs import *
from ._version import __version__

try:
    import subsurface.visualization
except ImportError:
    pass
