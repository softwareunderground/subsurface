import os

import dotenv

from subsurface.core.reader_helpers.readers_data import GenericReaderFilesHelper
from subsurface.modules.reader.wells.read_borehole_interface import read_collar

dotenv.load_dotenv()


def test_read_collar():
    reader: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG"),
        header=0,
        usecols=[0, 1, 2, 4],
        columns_map={
                "hole_id": "id", # ? Index name is not mapped
                "X_GK5_incl_inserted": "x",
                "Y__incl_inserted": "y",
                "Z_GK": "z"
        }
    )
    df = read_collar(reader)
    
    # TODO: df to unstruct
    
    pass
