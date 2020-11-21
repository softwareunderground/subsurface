from subsurface import TriSurf
from subsurface.io.topography import read_topography
from subsurface.visualization import to_pyvista_mesh, pv_plot


def test_read_topography_from_dxf(data_path):
    topo_path = data_path + '/topo/Topografia.dxf'
    unstruct = read_topography(topo_path)
    ts = TriSurf(mesh=unstruct)
    s = to_pyvista_mesh(ts)
    pv_plot([s], image_2d=False)
