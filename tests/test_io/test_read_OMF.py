import numpy as np
import pandas as pd
import pyvista
import omfvista
from dotenv import dotenv_values

import pytest

import subsurface
from subsurface import TriSurf
from subsurface.visualization import to_pyvista_mesh, pv_plot
from subsurface.writer import base_structs_to_binary_file


@pytest.fixture(scope="module")
def load_omf():
    config = dotenv_values()
    path = config.get('PATH_TO_OMF')
    omf = omfvista.load_project(path)
    return omf


def test_read_omf_with_pyvista(load_omf):
    omf = load_omf
    omf.plot(multi_colors=True, show_edges=True, notebook=False)


def test_omf_to_unstruct_single_block(load_omf):
    omf = load_omf
    polydata_obj: pyvista.PolyData = omf["GSB - BIF contacts"]
    unstruct_pyvista: pyvista.UnstructuredGrid = polydata_obj.cast_to_unstructured_grid()
    cells_pyvista = unstruct_pyvista.cells.reshape(-1, 4)[:, 1:]

    unstruct: subsurface.UnstructuredData = subsurface.UnstructuredData.from_array(
        vertex=unstruct_pyvista.points,
        cells=cells_pyvista,
    )

    base_structs_to_binary_file("leapfrog1", unstruct)

    ts = TriSurf(mesh=unstruct)
    s = to_pyvista_mesh(ts)
    pv_plot([s], image_2d=False)


def test_omf_to_unstruct_all_surfaces(load_omf):
    omf = load_omf
    list_of_polydata: list[pyvista.PolyData] = []
    for i in range(omf.n_blocks):
        block: pyvista.PolyData = omf[i]
        cell_type = block.cell_type(0)
        if cell_type == pyvista.CellType.TRIANGLE:
            pyvista_unstructured_grid: pyvista.UnstructuredGrid = block.cast_to_unstructured_grid()

            # * Create the unstructured data
            unstructured_data = subsurface.UnstructuredData.from_array(
                vertex=pyvista_unstructured_grid.points,
                cells=pyvista_unstructured_grid.cells.reshape(-1, 4)[:, 1:],
            )

            base_structs_to_binary_file(omf.get_block_name(i), unstructured_data)
            
            # * Convert subsurface object to pyvista again for plotting
            ts: subsurface.TriSurf = TriSurf(mesh=unstructured_data)
            s: pyvista.PolyData = to_pyvista_mesh(ts)

            list_of_polydata.append(s)

    pv_plot(list_of_polydata, image_2d=False)