import pyvista as pv

from subsurface.reader.mesh.obj_reader import plot_obj_with_multiple_textures


def test_read_obj():
    path_to_obj = ""
    reader = pv.get_reader(path_to_obj)
    mesh = reader.read()
    mesh.plot()
    
    
def test_read_obj_with_texture():
    path_to_obj = ""
    path_to_mtl = ""
    plot_obj_with_multiple_textures(
        obj_path=path_to_obj,
        mtl_path=path_to_mtl
    )