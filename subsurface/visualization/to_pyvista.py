from subsurface.structs.common import Common
from subsurface.structs.errors import PyVistaImportError
import numpy as np

try:
    import pyvista as pv
except ImportError:
    raise PyVistaImportError()


def to_pyvista_points(unstructured_element: Common):
    poly = pv.PolyData(unstructured_element.data.vertex)
    poly.point_arrays.update(unstructured_element.data.attributes_to_dict)


def to_pyvista_mesh(self):

    vertices = self.points.values
    faces = self.triangles.values
    faces = np.c_[np.full(len(faces), 3), faces]
    mesh = pv.PolyData(vertices, faces)
    mesh.point_arrays.update(self.point_data_dict)
    mesh.cell_arrays.update(self.cell_data_dict)
    return mesh


def to_pyvista_line(self):
    vertices = self.points.values
    lines = self.segments.values
    lines = np.c_[np.full(len(lines), 2), lines]
    lineset = pv.PolyData()
    lineset.points = vertices
    lineset.line = lines
    lineset.point_arrays.update(self.point_data_dict)
    lineset.cell_arrays.update(self.cell_data_dict)
    return lineset


def to_pyvista_tetra(self):
    try:
        import vtk
    except:
        raise PyVistaImportError()
    vertices = self.points.values
    tets = self.tetrahedrals.values
    cells = np.c_[np.full(len(tets), 4), tets]
    ctypes = np.array([vtk.VTK_TETRA, ], np.int32)
    mesh = pv.UnstructuredGrid(cells, ctypes, vertices)
    mesh.point_arrays.update(self.point_data_dict)
    mesh.cell_arrays.update(self.cell_data_dict)
    return mesh