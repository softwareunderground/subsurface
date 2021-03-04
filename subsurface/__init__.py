import subsurface.reader
import subsurface.interfaces
import subsurface.writer
from subsurface.structs import *
from ._version import __version__

try:
    from subsurface import visualization
except ImportError:
    pass

if __name__ == '__main__':
    pass
