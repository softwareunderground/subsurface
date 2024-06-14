from dataclasses import dataclass
from typing import Optional, List
import numpy as np


__all__ = ['RexMesh', 'RexMaterial', 'RexLineSet']


@dataclass
class RexMesh:
    """Data structure that can be converted to rex binary. Represent
     a Datatype Mesh"""
    name: str
    vertex: np.ndarray
    edges: np.ndarray
    normals: Optional[np.ndarray] = np.array([])
    texture: Optional[np.ndarray] = np.array([])
    color: Optional[np.ndarray] = np.array([])
    material_id: Optional[int] = np.array([])

    @property
    def ver_ravel(self):
        return self.vertex.ravel().astype('float32')

    @property
    def tri_ravel(self):
        return self.edges.ravel().astype('int32')

    @property
    def color_ravel(self):
        return self.color.ravel()

    @property
    def n_vtx(self):
        return self.ver_ravel.shape[0]

    @property
    def n_triangles(self):
        return self.tri_ravel.shape[0]

    @property
    def n_color(self):
        return self.color_ravel.shape[0]


@dataclass
class RexMaterial:
    # ambient
    ka_red: float = 1
    ka_green: float = 1
    ka_blue: float = 1
    # specular
    ks_red: float = 1
    ks_green: float = 1
    ks_blue: float = 1

    # difuse
    kd_red: float = 1
    kd_green: float = 1
    kd_blue: float = 1

    # textures
    ka_texture_ID: int = 9223372036854775807
    ks_texture_ID: int = 9223372036854775807
    kd_texture_ID: int = 9223372036854775807

    ns: float = 0.1  # specular exponent
    alpha: float = 1


@dataclass
class RexLineSet:
    foo: int

