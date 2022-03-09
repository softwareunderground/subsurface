import numpy as np
import pyvista as pv
from pyvista import UnstructuredGrid
from scipy.interpolate import griddata


def test_read_vtk():
    address = r"C:\Users\legui\OneDrive - Terranigma Solutions GmbH\Documents\Products and Services\LiquidEarth\Test Data Sets\ET\DeepERT_Hombourg.vtk"
    mesh: UnstructuredGrid = pv.read(address)
    point_data_mesh = mesh.cell_data_to_point_data()

    vertex = np.array(point_data_mesh.points)
    cell = np.array(point_data_mesh.cells)

    attributes_names = point_data_mesh.array_names
    point_arrays = point_data_mesh.point_arrays

    bounds = mesh.bounds
    x = np.linspace(bounds[0], bounds[1], 100)
    y = np.linspace(bounds[2], bounds[3], 100)
    z = np.linspace(bounds[4], bounds[5], 100)
    xg, yg, zg = np.meshgrid(x, y, z, indexing='ij', sparse=False)
    point_array = point_arrays[attributes_names[0]]
    grid_z2 = griddata(vertex, point_array, (xg, yg, zg), method='nearest')

    mesh.plot()