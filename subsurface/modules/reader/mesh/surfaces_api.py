import pandas as pd
from typing import Union

import numpy as np
import warnings

from .surface_reader import read_mesh_file_to_vertex, read_mesh_file_to_cells, cells_from_delaunay, read_mesh_file_to_attr
from ....core.reader_helpers.reader_unstruct import ReaderUnstructuredHelper
from ....core.structs import UnstructuredData


from ....core.structs.base_structures.unstructured_data import SpecialCellCase


def read_2d_mesh_to_unstruct(
        reader_args: ReaderUnstructuredHelper,
        delaunay: bool = True
) -> UnstructuredData:
    
    vertex: np.ndarray = read_mesh_file_to_vertex(reader_args.reader_vertex_args)
    cells: Union[np.ndarray, SpecialCellCase]
    cells_attr: Union[pd.DataFrame, None] = None
    vertex_attr: Union[pd.DataFrame, None] = None
    if reader_args.reader_cells_args is not None:
        cells = read_mesh_file_to_cells(reader_args.reader_cells_args)
    elif delaunay:
        cells = cells_from_delaunay(vertex)
    else:
        warnings.warn("No arguments to compute cell")
        cells = SpecialCellCase.POINTS
    if reader_args.reader_cells_attr_args is not None:
        cells_attr = read_mesh_file_to_attr(reader_args.reader_cells_attr_args)
    if reader_args.reader_vertex_attr_args is not None:
        vertex_attr = read_mesh_file_to_attr(reader_args.reader_vertex_attr_args)

    ud = UnstructuredData.from_array(
        vertex=vertex,
        cells=cells,
        cells_attr=cells_attr,
        vertex_attr=vertex_attr,
    )
    return ud
