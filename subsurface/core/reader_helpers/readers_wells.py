from typing import List

from dataclasses import dataclass

from subsurface.core.reader_helpers.readers_data import ReaderFilesHelper


@dataclass
class ReaderWellsHelper:
    reader_collars_args: ReaderFilesHelper
    reader_survey_args: ReaderFilesHelper
    reader_lith_args: ReaderFilesHelper = None
    reader_attr_args: List[ReaderFilesHelper] = None
