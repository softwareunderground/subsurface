from .well_files_reader import read_borehole_files, read_collar, read_lith, read_survey
from .pandas_to_welly import WellyToSubsurfaceHelper
# from .welly_reader import welly_to_subsurface
from subsurface.reader.wells.wells_utils import add_tops_from_base_and_altitude_in_place
from .. import ReaderFilesHelper
from ... import UnstructuredData


def borehole_location_to_unstruct(reader_helper: ReaderFilesHelper,
                                  add_number_segments: bool = True) -> UnstructuredData:
    from . import _wells_api
    return _wells_api.borehole_location_to_unstruct(reader_helper, add_number_segments)
    