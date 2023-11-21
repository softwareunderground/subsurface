import io

from subsurface.optional_dependencies import require_omf, require_pyvista
from subsurface.structs.unstructured_elements import UnstructuredData


def omf_stream_to_unstructs(stream: io.BytesIO) -> list[UnstructuredData]:
    pyvista = require_pyvista()
    omfvista = require_omf()
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
            unstructured_data.data.attrs['name'] = omf.get_block_name(i)
            list_unstructs.append(unstructured_data)
    
    return list_unstructs