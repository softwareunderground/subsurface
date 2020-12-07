import pytest

from subsurface.structs import StructuredGrid
from subsurface.structs.base_structures import UnstructuredData, StructuredData
from subsurface.visualization.to_pyvista import to_pyvista_points, pv_plot, \
    to_pyvista_mesh, to_pyvista_line, to_pyvista_tetra, to_pyvista_grid
import xarray as xr

pv = pytest.importorskip("pyvista")


def test_pyvista_points(point_set):
    s = to_pyvista_points(point_set)
    pv_plot([s], image_2d=True)


def test_pyvista_tri_surf(tri_surf):
    s = to_pyvista_mesh(tri_surf)
    pv_plot([s], image_2d=True)


def test_pyvista_line_set(line_set):
    s = to_pyvista_line(line_set, as_tube=False)

    pv_plot([s], image_2d=True, add_mesh_kwargs={'line_width': 5})


def test_pyvista_tetra(tetra_set):
    s = to_pyvista_tetra(tetra_set)
    pv_plot([s], image_2d=True)


def test_pyvista_structured_grid(struc_data):
    xx, yy, zz = struc_data[0]
    geo_map, high = struc_data[1]
    x_coord, y_coord, z_coord = struc_data[2:]
    s = xr.Dataset({'lith': (["x", "y", 'z'], xx),
                    'porosity': (["x", "y", 'z'], yy),
                    'something_else': (["x", "y", 'z'], zz),
                    'geo_map': (['x', 'y'], geo_map)},
                   coords={'x': x_coord, 'y': y_coord, 'z': z_coord})
    # StructuredData from Dataset
    sd = StructuredData(s)
    sg = StructuredGrid(sd)
    s = to_pyvista_grid(sg, 'something_else')
    pv_plot([s], image_2d=True)

    s = to_pyvista_grid(sg, 'geo_map')
    pv_plot([s], image_2d=True)
