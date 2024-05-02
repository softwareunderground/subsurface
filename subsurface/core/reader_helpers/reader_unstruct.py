from dataclasses import dataclass

from subsurface.core.reader_helpers.readers_data import ReaderFilesHelper


@dataclass
class ReaderUnstructuredHelper:
    reader_vertex_args: ReaderFilesHelper
    reader_cells_args: ReaderFilesHelper = None
    reader_vertex_attr_args: ReaderFilesHelper = None
    reader_cells_attr_args: ReaderFilesHelper = None
