import os

import dotenv

from subsurface.core.reader_helpers.readers_data import GenericReaderFilesHelper
from subsurface.modules.reader.wells import read_collar

dotenv.load_dotenv()


def test_read_collar():
    reader: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG"),
        header=0,
        usecols=[0, 1, 2, 4]
    )
    df = read_collar(reader)
    pass
