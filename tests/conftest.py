import enum

import pytest

from subsurface.structs import PointSet, TriSurf, LineSet, TetraMesh
from subsurface.structs.base_structures import UnstructuredData
import numpy as np
import pandas as pd
import os
import functools


@enum.unique
class RequirementsLevel(enum.Enum):
    CORE = 2**1
    BASE = 2**2
    GEOSPATIAL = 2**4
    WELLS = 2**5
    DEV = 2**31
    READ_WELL = CORE | WELLS
    OPTIONAL = CORE | BASE | GEOSPATIAL | WELLS
    ALL = CORE | BASE | OPTIONAL | GEOSPATIAL | DEV

    @classmethod
    def REQUIREMENT_LEVEL_TO_TEST(cls):
        return cls.READ_WELL
    
    # Utility function to check if a flag is set
    def __or__(self, other):
        if isinstance(other, RequirementsLevel):
            return RequirementsLevel(self.value | other.value)
        return NotImplemented

    def __and__(self, other):
        if isinstance(other, RequirementsLevel):
            return RequirementsLevel(self.value & other.value)
        return NotImplemented

    def __xor__(self, other):
        if isinstance(other, RequirementsLevel):
            return RequirementsLevel(self.value ^ other.value)
        return NotImplemented

    def __invert__(self):
        return RequirementsLevel(~self.value & int(RequirementsLevel.ALL.value))

    @classmethod
    def is_set(cls, flag):
        return (cls.REQUIREMENT_LEVEL_TO_TEST().value & flag.value) == flag.value
    
    @classmethod
    def is_not_set(cls, flag):
        return (cls.REQUIREMENT_LEVEL_TO_TEST().value & flag.value) != flag.value

    # Utility to combine flags
    @staticmethod
    def combine(*flags):
        result = functools.reduce(lambda x, y: x | y, (flag.value for flag in flags))
        return RequirementsLevel(result)
    
    @classmethod    
    def check_requirements(cls, minimum_level):
        return cls.REQUIREMENT_LEVEL_TO_TEST().value < minimum_level.value



def check_requirements(minimum_level: RequirementsLevel):
    return RequirementsLevel.REQUIREMENT_LEVEL_TO_TEST().value < minimum_level.value


@pytest.fixture(scope='session')
def data_path():
    return os.path.abspath(os.path.dirname(__file__) + '/data')


@pytest.fixture(scope='session')
def unstruct_factory():
    foo = UnstructuredData.from_array(np.ones((5, 3)), np.ones((4, 3)), pd.DataFrame({'foo': np.arange(4)}))
    return foo


@pytest.fixture(scope='session')
def point_set():
    n = 100

    data = UnstructuredData.from_array(vertex=np.random.rand(n, 3), cells=np.random.rand(n, 0),
                                       cells_attr=pd.DataFrame({'foo': np.arange(n)}))

    pointset = PointSet(data)
    return pointset


@pytest.fixture(scope='session')
def tri_surf():
    vertices = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [1, 1, 0],
                         [0, 1, 0],
                         [0.5, 0.5, -1]])

    faces = np.vstack([[0, 1, 2],
                       [0, 1, 4],
                       [1, 2, 4]])

    data = UnstructuredData.from_array(vertex=vertices, cells=faces,
                                       cells_attr=pd.DataFrame({'foo': np.arange(faces.shape[0])}))
    trisurf = TriSurf(data)
    return trisurf


@pytest.fixture(scope='session')
def line_set():
    n = 100

    theta = np.linspace(-4 * np.pi, 4 * np.pi, 100)
    z = np.linspace(-2, 2, 100)
    r = z ** 2 + 1
    x = r * np.sin(theta)
    y = r * np.cos(theta)
    v = np.column_stack((x, y, z))

    data = UnstructuredData.from_array(vertex=v, cells="lines",
                                       cells_attr=pd.DataFrame({'foo': np.arange(n - 1)}))
    lineset = LineSet(data)
    lineset.generate_default_cells()
    return lineset


@pytest.fixture(scope='session')
def tetra_set():
    vertices = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [1, 1, 0],
                         [0, 1, 1]])
    cells = np.array([[0, 1, 2, 3], ])

    data = UnstructuredData.from_array(vertex=vertices, cells=cells,
                                       cells_attr=pd.DataFrame({'foo': np.arange(cells.shape[0])}))

    tets = TetraMesh(data)
    return tets


@pytest.fixture(scope='session')
def struc_data():
    xrng = np.arange(-10, 10, 5)
    yrng = np.arange(-10, 10, 7)
    zrng = np.arange(-10, 10, 2)
    grid_3d = np.meshgrid(xrng * 10, yrng * 100, zrng * 1000, indexing='ij')
    grid_2d = np.meshgrid(xrng * 20, yrng * 200, indexing='ij')
    return grid_3d, grid_2d, xrng, yrng, zrng
