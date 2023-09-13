import pyvista as pv
import numpy as np
import os


def plot_obj_with_multiple_textures(obj_path, mtl_path=None, texture_dir=None):
    obj_mesh = pv.read(obj_path)
    if mtl_path is None:
        # parse the obj file for mtl_path if the mtl_path is not set.
        pass
    if texture_dir is None:
        texture_dir = os.path.dirname(obj_path)

    texture_paths = []
    mtl_names = []

    # parse the mtl file
    with open(mtl_path) as mtl_file:
        for line in mtl_file.readlines():
            parts = line.strip().split()
            if len(parts) < 2:
                continue
            if parts[0] == 'map_Kd':
                texture_paths.append(os.path.join(texture_dir, parts[1]))
            elif parts[0] == 'newmtl':
                mtl_names.append(parts[1])

    plotter = pv.Plotter()
    material_ids = obj_mesh.cell_data['MaterialIds']

    # This part is not working.
    # for i in np.unique(material_ids):
    #     obj_mesh.textures[mtl_names[i]] = pv.read_texture(texture_paths[i])
    # plotter.add_mesh(obj_mesh)

    # This one do.
    for i in np.unique(material_ids):
        mesh_part = obj_mesh.extract_cells(material_ids == i)
        mesh_part.textures[mtl_names[i]] = pv.read_texture(texture_paths[i])
        plotter.add_mesh(mesh_part)
    plotter.show()