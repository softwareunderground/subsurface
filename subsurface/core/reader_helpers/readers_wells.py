from typing import List

from dataclasses import dataclass

from subsurface.core.reader_helpers.readers_data import GenericReaderFilesHelper


@dataclass
class ReaderWellsHelper:
    reader_collars_args: GenericReaderFilesHelper
    reader_survey_args: GenericReaderFilesHelper
    reader_lith_args: GenericReaderFilesHelper = None
    reader_attr_args: List[GenericReaderFilesHelper] = None
