from dataclasses import dataclass

from subsurface.core.reader_helpers.readers_data import GenericReaderFilesHelper


@dataclass
class ReaderUnstructuredHelper:
    reader_vertex_args: GenericReaderFilesHelper
    reader_cells_args: GenericReaderFilesHelper = None
    reader_vertex_attr_args: GenericReaderFilesHelper = None
    reader_cells_attr_args: GenericReaderFilesHelper = None
