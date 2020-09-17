import pytest
from subsurface.structs.base_structures import UnstructuredData
from subsurface.visualization.to_pyvista import to_pyvista_points, pv_plot, \
    to_pyvista_mesh, to_pyvista_line, to_pyvista_tetra

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
