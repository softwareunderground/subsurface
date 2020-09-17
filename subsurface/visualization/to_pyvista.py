from subsurface.structs.common import Common
from subsurface.structs.errors import PyVistaImportError
import numpy as np

try:
    import pyvista as pv
except ImportError:
    raise PyVistaImportError()


def pv_plot(meshes: list,
            image_2d=False,
            plotter_kwargs: dict = None,
            add_mesh_kwargs: dict = None):
    """

    :param meshes:
    :param image_2d: bool
        If True convert plot to matplotlib imshow. This helps for visualizing
        the plot in IDEs
    :param plotter_kwargs:
    :param add_mesh_kwargs:
    :return:
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


def to_pyvista_points(unstructured_element: Common, plot=False, image_2d=False):
    poly = pv.PolyData(unstructured_element.data.vertex)
    poly.point_arrays.update(unstructured_element.data.attributes_to_dict)
    if plot is True:
        pv_plot(poly, image_2d)

    return poly


def to_pyvista_mesh(unstructured_element):
    nve = unstructured_element.data.n_vertex_per_element
    vertices = unstructured_element.data.vertex
    edges = np.c_[np.full(unstructured_element.data.n_elements, nve),
                  unstructured_element.data.edges]
    mesh = pv.PolyData(vertices, edges)
    mesh.cell_arrays.update(unstructured_element.data.attributes_to_dict)
    return mesh


def to_pyvista_line(unstructured_element, as_tube=True, radius=None,
                    spline=False, n_interp_points=1000):

    nve = unstructured_element.data.n_vertex_per_element
    vertices = unstructured_element.data.vertex
    edges = np.c_[np.full(unstructured_element.data.n_elements, nve),
                  unstructured_element.data.edges]
    if spline is False:
        mesh = pv.PolyData()
        mesh.points = vertices
        mesh.lines = edges
    else:
        raise NotImplementedError
        # mesh = pv.Spline(ver)
    mesh.cell_arrays.update(unstructured_element.data.attributes_to_dict)
    if as_tube is True:
        return mesh.tube(radius=radius)
    else:
        return mesh


def to_pyvista_tetra(unstructured_element):

    vertices = unstructured_element.data.vertex
    tets = unstructured_element.data.edges
    cells = np.c_[np.full(len(tets), 4), tets]
    import vtk
    ctypes = np.array([vtk.VTK_TETRA, ], np.int32)
    mesh = pv.UnstructuredGrid(cells, ctypes, vertices)
    mesh.cell_arrays.update(unstructured_element.data.attributes_to_dict)
    return mesh