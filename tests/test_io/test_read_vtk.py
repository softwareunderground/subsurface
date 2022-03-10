import numpy as np
import pytest
import xarray as xr
import pandas as pd
import pyvista as pv
from pyvista import UnstructuredGrid
from scipy.interpolate import griddata

from subsurface import UnstructuredData, StructuredGrid
from subsurface.reader.volume.volume_utils import interpolate_unstructured_data_to_structured_data, InterpolationMethod
from subsurface.structs.base_structures.common_data_utils import replace_outliers
from subsurface.visualization import to_pyvista_grid, pv_plot

@pytest.mark.skip(reason="We need a small vtk file to add to the project for this.")
def test_read_vtk():
    address = r"C:\Users\legui\OneDrive - Terranigma Solutions GmbH\Documents\Products and Services\LiquidEarth\Test Data Sets\ET\DeepERT_Hombourg.vtk"
    mesh: UnstructuredGrid = pv.read(address)
    
    point_data_mesh = mesh.cell_data_to_point_data()

    vertex = np.array(point_data_mesh.points)
    cell = np.array(point_data_mesh.cells)

    attributes_names = point_data_mesh.array_names
    point_arrays = point_data_mesh.point_arrays

    bounds = mesh.bounds

    # Create dictionary with attributes
    attributes_dict = {}
    for attribute in attributes_names:
        attributes_dict[attribute] = point_arrays[attribute]

    vertex_attr = pd.DataFrame(attributes_dict)
    unstructure_data = UnstructuredData.from_array(vertex, "points", vertex_attr=vertex_attr)
    
    structure_data = interpolate_unstructured_data_to_structured_data(
        unstructure_data, attributes_names[0], interpolation_method=InterpolationMethod.nearest)
    
    sg = StructuredGrid(structure_data)

    mesh_g = to_pyvista_grid(sg)
    pv_plot([mesh_g], image_2d=False)
