from typing import Union

from subsurface.structs import PointSet, TriSurf, LineSet, TetraMesh, StructuredGrid
from subsurface.structs.common import Common
from subsurface.structs.errors import PyVistaImportError
import numpy as np

try:
    import pyvista as pv
except ImportError:
    raise ImportError()


def pv_plot(meshes: list,
            image_2d=False,
            plotter_kwargs: dict = None,
            add_mesh_kwargs: dict = None):
    """

    Args:
        meshes (List[pv.PolyData]):
        image_2d (bool): If True convert plot to matplotlib imshow. This helps for visualizing
         the plot in IDEs
        plotter_kwargs (dict): pyvista.Plotter kwargs
        add_mesh_kwargs (dict): pyvista.add_mesh kwargs

    """

    plotter_kwargs = dict() if plotter_kwargs is None else plotter_kwargs
    add_mesh_kwargs = dict() if add_mesh_kwargs is None else add_mesh_kwargs

    p = pv.Plotter(**plotter_kwargs, off_screen=image_2d)

    for m in meshes:
        p.add_mesh(m, **add_mesh_kwargs)

    if image_2d is False:
        return p.show()

    else:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError('Matplotlib is necessary for generating a 2D image.')
        img = p.plot(screenshot=True)
        fig = plt.imshow(img[1])
        plt.axis('off')
        plt.show()
        p.close()
        return fig


def to_pyvista_points(point_set: PointSet):
    """Create pyvista.PolyData from PointSet

    Args:
        point_set (PointSet): Class for pointset based data structures.

    Returns:
        pv.PolyData
    """
    poly = pv.PolyData(point_set.data.vertex)
    poly.point_arrays.update(point_set.data.attributes_to_dict)

    return poly


def to_pyvista_mesh(unstructured_element: Union[TriSurf]) -> pv.PolyData:
    """Create planar surface PolyData from unstructured element such as TriSurf
    """
    nve = unstructured_element.data.n_vertex_per_element
    vertices = unstructured_element.data.vertex
    edges = np.c_[np.full(unstructured_element.data.n_elements, nve),
                  unstructured_element.data.edges]
    mesh = pv.PolyData(vertices, edges)
    mesh.cell_arrays.update(unstructured_element.data.attributes_to_dict)
    mesh.point_arrays.update(unstructured_element.data.points_attributes)
    return mesh


def to_pyvista_line(line_set: LineSet, as_tube=True, radius=None,
                    spline=False, n_interp_points=1000):
    """Create pyvista PolyData for 1D lines

    Args:
        line_set:
        as_tube (bool):
        radius (float): radius of the tube
        spline: NotImplemented
        n_interp_points: NotImplemented

    Returns:
        pv.PolyData
    """
    nve = line_set.data.n_vertex_per_element
    vertices = line_set.data.vertex
    edges = np.c_[np.full(line_set.data.n_elements, nve),
                  line_set.data.edges]
    if spline is False:
        mesh = pv.PolyData()
        mesh.points = vertices
        mesh.lines = edges
    else:
        raise NotImplementedError
        # mesh = pv.Spline(ver)
    mesh.cell_arrays.update(line_set.data.attributes_to_dict)
    if as_tube is True:
        return mesh.tube(radius=radius)
    else:
        return mesh


def to_pyvista_tetra(tetra_mesh: TetraMesh):
    """Create pyvista.UnstructuredGrid"""
    vertices = tetra_mesh.data.vertex
    tets = tetra_mesh.data.edges
    cells = np.c_[np.full(len(tets), 4), tets]
    import vtk
    ctypes = np.array([vtk.VTK_TETRA, ], np.int32)
    mesh = pv.UnstructuredGrid(cells, ctypes, vertices)
    mesh.cell_arrays.update(tetra_mesh.data.attributes_to_dict)
    return mesh


def to_pyvista_grid(structured_grid: StructuredGrid, attribute: str):
    ndim = structured_grid.ds.data[attribute].ndim
    if ndim == 2:
        meshgrid = structured_grid.meshgrid_2d(attribute)
    elif ndim == 3:
        meshgrid = structured_grid.meshgrid_3d
    else:
        raise AttributeError('The DataArray does not have valid dimensionality.')

    mesh = pv.StructuredGrid(*meshgrid)
    mesh.point_arrays.update({attribute: structured_grid.ds.data[attribute].values.ravel()})

    return mesh