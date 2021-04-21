from typing import Union, Tuple, Optional

from subsurface.structs import PointSet, TriSurf, LineSet, TetraMesh, StructuredGrid
import numpy as np

try:
    import pyvista as pv
except ImportError:
    raise ImportError()

try:
    from pyvistaqt import BackgroundPlotter

    background_plotter_imported = True
except ImportError:
    background_plotter_imported = False


__all__ = ['pv_plot', 'to_pyvista_points', 'to_pyvista_mesh',
           'to_pyvista_mesh_and_texture', 'to_pyvista_line',
           'to_pyvista_tetra', 'to_pyvista_grid', 'update_grid_attribute']


def pv_plot(meshes: list,
            image_2d=False,
            ve=None,
            plotter_kwargs: dict = None,
            add_mesh_kwargs: dict = None,
            background_plotter=False):
    """Function to plot meshes in vtk using pyvista

    Args:
        meshes (List[pv.PolyData]):
        image_2d (bool): If True convert plot to matplotlib imshow. This helps for visualizing
         the plot in IDEs
        ve (float): vertical exaggeration
        plotter_kwargs (dict): pyvista.Plotter kwargs
        add_mesh_kwargs (dict): pyvista.add_mesh kwargs
        background_plotter (bool): if true and pyvistaqt installed use pyvista
         backgroung plotter.
    """

    plotter_kwargs = dict() if plotter_kwargs is None else plotter_kwargs
    add_mesh_kwargs = dict() if add_mesh_kwargs is None else add_mesh_kwargs

    if background_plotter is True:
        if background_plotter_imported is True:
            p = BackgroundPlotter(**plotter_kwargs, off_screen=image_2d)
        else:
            raise ImportError(
                'You need to install pyvistaqt for using this plotter.')
    else:
        off_screen = True if image_2d is True else None
        p = pv.Plotter(**plotter_kwargs, off_screen=off_screen)

    if ve is not None:
        p.set_scale(zscale=ve)

    for m in meshes:
        p.add_mesh(m, **add_mesh_kwargs)

    p.show_bounds()

    if image_2d is False:
        p.show()
        return p

    else:
        try:
            import matplotlib.pyplot as plt
        except ImportError:
            raise ImportError('Matplotlib is necessary for generating a 2D image.')
        img = p.show(screenshot=True)
        fig = plt.imshow(img[1])
        plt.axis('off')
        plt.show(block=False)
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


def to_pyvista_mesh(unstructured_element: Union[TriSurf],
                    ) -> pv.PolyData:
    """Create planar surface PolyData from unstructured element such as TriSurf

    Returns:
        mesh texture
    """
    nve = unstructured_element.mesh.n_vertex_per_element
    vertices = unstructured_element.mesh.vertex
    cells = np.c_[np.full(unstructured_element.mesh.n_elements, nve),
                  unstructured_element.mesh.cells]
    mesh = pv.PolyData(vertices, cells)
    mesh.cell_arrays.update(unstructured_element.mesh.attributes_to_dict)
    mesh.point_arrays.update(unstructured_element.mesh.points_attributes)

    return mesh


def to_pyvista_mesh_and_texture(triangular_surface: Union[TriSurf], ) -> Tuple[pv.PolyData, Optional[np.array]]:
    """Create planar surface PolyData from unstructured element such as TriSurf

    Returns:
        mesh texture
    """
    mesh = to_pyvista_mesh(triangular_surface)

    if triangular_surface.texture is None:
        raise ValueError('unstructured_element needs texture data to be mapped.')

    mesh.texture_map_to_plane(
        inplace=True,
        origin=triangular_surface.texture_origin,
        point_u=triangular_surface.texture_point_u,
        point_v=triangular_surface.texture_point_v
    )
    tex = pv.numpy_to_texture(triangular_surface.texture.values)
    mesh._textures = {0: tex}

    from vtkmodules.util.numpy_support import vtk_to_numpy
    uv = vtk_to_numpy(mesh.GetPointData().GetTCoords())
    return mesh, uv


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
    cells = np.c_[np.full(line_set.data.n_elements, nve),
                  line_set.data.cells]
    if spline is False:
        mesh = pv.PolyData()
        mesh.points = vertices
        mesh.lines = cells
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
    tets = tetra_mesh.data.cells
    cells = np.c_[np.full(len(tets), 4), tets]
    import vtk
    ctypes = np.array([vtk.VTK_TETRA, ], np.int32)
    mesh = pv.UnstructuredGrid(cells, ctypes, vertices)
    mesh.cell_arrays.update(tetra_mesh.data.attributes_to_dict)
    return mesh


def to_pyvista_grid(structured_grid: StructuredGrid,
                    data_set_name: str = None,
                    attribute_slice: dict = None,
                    data_order: str = 'F'):
    """

    Args:
        structured_grid:
        data_set_name:
        attribute_slice: dictionary to select which 3D array will be displayed as color

    Returns:

    """
    if attribute_slice is None:
        attribute_slice = dict()

    if data_set_name is None:
        data_set_name = structured_grid.ds.data_array_name

    cart_dims = structured_grid.cartesian_dimensions
    data_dims = structured_grid.ds.data[data_set_name].sel(
        **attribute_slice
    ).ndim
    if cart_dims < data_dims:
        raise AttributeError('Data dimension and cartesian dimensions must match.'
                             'Possibly there are not valid dimension name in the'
                             'xarray.DataArray. These are X Y Z x y z')

    if data_dims == 2:
        meshgrid = structured_grid.meshgrid_2d(data_set_name)
    elif data_dims == 3:
        meshgrid = structured_grid.meshgrid_3d
    else:
        raise AttributeError('The DataArray does not have valid dimensionality. '
                             'Possibly there are not valid dimension name in the'
                             'xarray.DataArray. These are X Y Z x y z')

    mesh = pv.StructuredGrid(*meshgrid)
    update_grid_attribute(mesh, structured_grid, data_order,
                          attribute_slice, data_set_name)

    return mesh


def update_grid_attribute(mesh, structured_grid,
                          data_order='F',
                          attribute_slice=None,
                          data_set_name=None):
    if attribute_slice is None:
        attribute_slice = dict()

    if data_set_name is None:
        data_set_name = structured_grid.ds.data_array_name

    mesh.point_arrays.update(
        {data_set_name: structured_grid.ds.data[data_set_name].sel(
            **attribute_slice
        ).values.ravel(data_order)})

    return mesh


def _n_cartesian_coord(attribute, structured_grid):
    coord_names = np.array(['X', 'Y', 'Z', 'x', 'y', 'z'])
    ndim = np.isin(coord_names, structured_grid.ds.data[attribute].dims).sum()
    return ndim
