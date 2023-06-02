from typing import TextIO

import omfvista
import pyvista

from subsurface.structs.unstructured_elements import UnstructuredData


def omf_stream_to_unstructs(stream: TextIO) -> list[UnstructuredData]:
    omf = omfvista.load_project(stream)
    list_unstructs: list[UnstructuredData] = []
    for i in range(omf.n_blocks):
        block: pyvista.PolyData = omf[i]
        cell_type = block.cell_type(0)
        if cell_type == pyvista.CellType.TRIANGLE:
            pyvista_unstructured_grid: pyvista.UnstructuredGrid = block.cast_to_unstructured_grid()

            # * Create the unstructured data
            unstructured_data = UnstructuredData.from_array(
                vertex=pyvista_unstructured_grid.points,
                cells=pyvista_unstructured_grid.cells.reshape(-1, 4)[:, 1:],
            )
            
            list_unstructs.append(unstructured_data)
    
    return list_unstructs