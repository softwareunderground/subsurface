import pyvista as pv

from subsurface.reader.mesh.obj_reader import plot_obj_with_multiple_textures


def test_read_obj():
    path_to_obj = "/mnt/d/OneDrive - Terranigma Solutions GmbH/Documents/Projects/VGC/Models/Broadhaven_Obj/model/model.obj"
    reader = pv.get_reader(path_to_obj)
    mesh = reader.read()
    mesh.plot()
    
    
def test_read_obj_with_texture():
    path_to_obj = "/mnt/d/OneDrive - Terranigma Solutions GmbH/Documents/Projects/VGC/Models/Broadhaven_Obj/model/model.obj"
    path_to_mtl = "/mnt/d/OneDrive - Terranigma Solutions GmbH/Documents/Projects/VGC/Models/Broadhaven_Obj/model/model.mtl"
    plot_obj_with_multiple_textures(
        obj_path=path_to_obj,
        mtl_path=path_to_mtl
    )