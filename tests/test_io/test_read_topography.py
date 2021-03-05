import pytest

from subsurface import TriSurf, StructuredGrid
from subsurface.reader import read_structured_topography, read_unstructured_topography
from subsurface.structs.base_structures.common_data_utils import replace_outliers
from subsurface.visualization import to_pyvista_mesh, pv_plot, to_pyvista_grid


def test_read_topography_from_dxf(data_path):
    topo_path = data_path + '/topo/Topografia.dxf'
    unstruct = read_unstructured_topography(topo_path)
    ts = TriSurf(mesh=unstruct)
    s = to_pyvista_mesh(ts)
    pv_plot([s], image_2d=True)


def test_read_topography_from_tif(data_path):
    topo_path = data_path + '/topo/dtm_rp.tif'
    struct = read_structured_topography(topo_path)
    replace_outliers(struct, 'topography', 0.99)
    sg = StructuredGrid(struct)
    s = to_pyvista_grid(sg, data_order='C', data_set_name='topography')
    pv_plot([s], image_2d=True)
