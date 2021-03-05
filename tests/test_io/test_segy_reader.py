from typing import List, Union

import pytest
import os
import pandas as pd
import geopandas as gpd
from subsurface import StructuredGrid, TriSurf
from subsurface.geological_formats import segy_reader
from subsurface.reader.profiles.profiles_core import create_mesh_from_trace
from subsurface.structs.base_structures import StructuredData, UnstructuredData
import matplotlib.pyplot as plt
import numpy as np
import pyvista as pv
import imageio

from subsurface.visualization import to_pyvista_mesh, pv_plot

segyio = pytest.importorskip('segyio')

input_path = os.path.dirname(__file__) + '/../data/segy'
files = ['/E5_MIG_DMO_FINAL.sgy', '/E5_MIG_DMO_FINAL_DEPTH.sgy', '/E5_STACK_DMO_FINAL.sgy', '/test.segy']
images = ['/myplot_cropped.png', '/myplot2_cropped.png', '/myplot3_cropped.png', '/myplot4_cropped.png']
# all files are unstructured: only raw data reading and writing is supported by segyio

coords_file = input_path + '/E5_CMP_COORDS.txt'
coords = {}
with open(coords_file, 'r') as cf:
    lines = cf.readlines()
    xs = []
    ys = []
    for line in lines:
        x = line.split()[1]
        y = line.split()[2]
        xs.append(x)
        ys.append(y)
coords = {'x': xs, 'y': ys}
# coords = input_path + '/E5_CMP_COORDS.csv'


@pytest.fixture(scope="module")
def get_structured_data() -> List[StructuredData]:
    file_array = [input_path + x for x in files]
    sd_array = [segy_reader.read_in_segy(fp) for fp in file_array]
    return sd_array


@pytest.fixture(scope="module")
def get_images() -> List[str]:
    image_array = [input_path + y for y in images]
    return image_array


def test_converted_to_structured_data(get_structured_data):
    for x in get_structured_data:
        assert isinstance(x, StructuredData)
        x.default_dataset.plot()
        plt.show(block=False)


def test_pyvista_grid(get_structured_data, get_images):
    for s, t in zip(get_structured_data, get_images):

        x = s.data['x']
        y = s.data['y']

        x2, y2 = np.meshgrid(x, y)
        print(x2, y2)
        tex = pv.read_texture(t)
        z = np.zeros((len(y),len(x)))
        # z.reshape(z, (-1, 1101))
        print(x2.shape, y2.shape, z.shape)

        # create a surface to host this texture
        surf = pv.StructuredGrid(z, x2, y2)
        print(surf)

        surf.texture_map_to_plane(inplace=True)
        pv_plot([surf], image_2d=True)

        # use Trisurf with Structured Data for texture and UnstructuredData for geometry


def test_read_segy_to_struct_data_imageio(get_structured_data, get_images):
    for x, image in zip(get_structured_data, get_images):
        vertex = np.array([[0, x.data['x'][0], x.data['y'][0]], [0, x.data['x'][-1], x.data['y'][0]], [0, x.data['x'][0], x.data['y'][-1]], [0, x.data['x'][-1], x.data['y'][-1]]])
        # vertex = np.array([[0, coords['x'][0], coords['y'][0]], [0, coords['x'][-1], coords['y'][-1]], [0, coords['x'][0], coords['y'][0]], [0, coords['x'][0], coords['y'][0]]])
        # [print(s) for s in vertex]
        import pyvista as pv
        a = pv.PolyData(vertex)
        b = a.delaunay_2d().faces
        cells = b.reshape(-1, 4)[:, 1:]
        print('cells', cells)
        struct = StructuredData.from_numpy(np.array(imageio.imread(image)))
        unstruct = UnstructuredData.from_array(vertex, cells)
        ts = TriSurf(
            mesh=unstruct,
            texture=struct
            # texture_point_u=point_u,
            # texture_point_v=point_v
        )

        s = to_pyvista_mesh(ts)
        pv_plot([s], image_2d=True)


def test_plot_segy_as_struct_data_with_coords_dict(get_structured_data, get_images):
    for x, image in zip(get_structured_data, get_images):
        zmin = -6000.0
        zmax = 0.0
        v, e = segy_reader.create_mesh_from_coords(coords, zmin, zmax)

        struct = StructuredData.from_numpy(np.array(imageio.imread(image)))
        print(struct) # normalize to number of samples
        unstruct = UnstructuredData.from_array(v, e)

        origin = [float(coords['x'][0]), float(coords['y'][0]), zmin]
        point_u = [float(coords['x'][-1]), float(coords['y'][-1]), zmin]
        point_v = [float(coords['x'][0]), float(coords['y'][0]), zmax]
        ts = TriSurf(
            mesh=unstruct,
            texture=struct,
            texture_origin=origin,
            texture_point_u=point_u,
            texture_point_v=point_v
        )

        s = to_pyvista_mesh(ts)
        pv_plot([s], image_2d=True)
