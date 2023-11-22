import pyvista as pv
from dotenv import dotenv_values


config = dotenv_values()
path_to_obj = config.get('PATH_TO_OBJ')
path_to_mtl = config.get('PATH_TO_MTL')


def test_read_obj():
    reader = pv.get_reader(path_to_obj)
    mesh = reader.read()
    mesh.plot()
    
    