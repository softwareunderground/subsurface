import subsurface.modules.reader
import subsurface.api.interfaces
import subsurface.modules.writer
from . import core
from .modules import visualization
from subsurface.core.structs import *
from datetime import datetime
import dotenv

dotenv.load_dotenv()

try:
    from subsurface import visualization
except ImportError:
    pass

# Version.
try:
    # - Released versions just tags:       0.8.0
    # - GitHub commits add .dev#+hash:     0.8.1.dev4+g2785721
    # - Uncommitted changes add timestamp: 0.8.1.dev4+g2785721.d20191022
    from ._version import version as __version__
except ImportError:
    # If it was not installed, then we don't know the version. We could throw a
    # warning here, but this case *should* be rare. subsurface should be
    # installed properly!
    __version__ = 'unknown-'+datetime.today().strftime('%Y%m%d')

if __name__ == '__main__':
    pass
