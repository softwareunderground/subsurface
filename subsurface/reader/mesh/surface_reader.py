from typing import Union, Callable, List, Dict

import pandas as pd
from pandas._typing import FilePathOrBuffer

from subsurface.reader.readers_data import ReaderDataUnstructured, RawDataUnstructured, RawDataOptions, ReaderDataArgs
from subsurface.structs.base_structures import UnstructuredData
from subsurface.utils.utils_core import get_extension
import numpy as np
import xarray as xr
from scipy.spatial.qhull import Delaunay


def read_2d_mesh(reader_args: ReaderDataUnstructured, raw_data_options: RawDataOptions = None,
                 delaunay: bool = True) -> UnstructuredData:
    """
    Reads in csv files with n table columns and returns UnstructuredData object. m cells have to be in m columns named
    with the order of the points. If no cells are present default ones are generated.

    Vertex will be read from columns named x, y, z and cells from e1, e2, e3. You can use columns_map to map the required
    column names to any other name.

    Args:
        path_to_file (str): Filepath.
        columns_map (dict): Dictionary with format: {'csv_columns_name1': 'x', 'csv_columns_name2': 'y', ...}
        attribute_cols (dict ()): t-element dict with the column names as keys and the column indices as the values
        delaunay (bool): If True compute cells using vtk Dalauny algorithm.
        swap_yz (bool): If True swap yz axis (left hand to right hand coord system).
        reader_kwargs: `pandas.read_csv` kwargs
    Returns:
        (UnstructuredData) csv with n columns stored in pandas.DataFrame of vertices with
        3 columns (3d vertices), cells of m columns forming an m-sided polygon and pandas.DataFrame of attributes with n-(m+3) columns.

    """
    if raw_data_options is None:
        raw_data_options = RawDataOptions()

    raw_data = RawDataUnstructured()
    raw_data.vertex = read_mesh_file_to_vertex(reader_args.reader_vertex_args)
    if reader_args.reader_cells_args is not None:
        raw_data.cells = read_mesh_file_to_cells(reader_args.reader_cells_args)
    elif delaunay:
        raw_data.cells = cells_from_delaunay(raw_data.vertex)
    else:
        raise ValueError("No arguments to compute cell")
    if reader_args.reader_cells_attr_args is not None:
        raw_data.cells_attr = read_mesh_file_to_attr(reader_args.reader_cells_attr_args)
    if reader_args.reader_vertex_attr_args is not None:
        raw_data.vertex_attr = read_mesh_file_to_attr(reader_args.reader_vertex_attr_args)

    if raw_data_options.swap_yz_cells: raw_data.swap_yz_col_cells()
    ud = UnstructuredData.from_raw_data(raw_data)
    return ud


def read_mesh_file_to_vertex(reader_args: ReaderDataArgs) -> np.ndarray:
    extension = get_extension(reader_args.file_or_buffer)
    if extension == '.csv':
        vertex = mesh_csv_to_vertex(reader_args.file_or_buffer, reader_args.columns_map,
                                    **reader_args.pandas_reader_kwargs)
    elif extension == '.dxf':
        vertex = dxf_to_vertex(reader_args.file_or_buffer)
    else:
        raise ValueError(f"Subsurface is not able to read the following extension: {extension}")
    return vertex


def read_mesh_file_to_cells(reader_args: ReaderDataArgs) -> np.ndarray:
    extension = get_extension(reader_args.file_or_buffer)
    if extension == '.csv':
        cells = mesh_csv_to_cells(reader_args.file_or_buffer, reader_args.columns_map,
                                  **reader_args.pandas_reader_kwargs)
    else:
        raise ValueError(f"Subsurface is not able to read the following extension: {extension}")
    return cells


def read_mesh_file_to_attr(reader_args: ReaderDataArgs):
    extension = get_extension(reader_args.file_or_buffer)
    if extension == ".csv":
        attr = mesh_csv_to_attributes(reader_args.file_or_buffer,
                                      reader_args.columns_map,
                                      **reader_args.pandas_reader_kwargs)
    else:
        raise ValueError(f"Subsurface is not able to read the following extension: {extension}")
    return attr


def mesh_csv_to_vertex(path_to_file: str, columns_map: Union[None, Callable, dict, pd.Series] = None,
                       **reader_kwargs) -> np.ndarray:
    data = pd.read_csv(path_to_file, **reader_kwargs)
    if columns_map is not None: map_columns_names(columns_map, data)
    return get_vertices_from_df(data)


def mesh_csv_to_cells(path_to_file: str, columns_map: Union[None, Callable, dict, pd.Series] = None,
                      **reader_kwargs) -> np.ndarray:
    data = pd.read_csv(path_to_file, **reader_kwargs)
    if columns_map is not None: map_columns_names(columns_map, data)
    return get_cells_from_df(data)


def mesh_csv_to_attributes(path_to_file: str,
                           columns_map: Union[None, Callable, dict, pd.Series] = None,
                           **reader_kwargs) -> pd.DataFrame:

    data = pd.read_csv(path_to_file, **reader_kwargs)
    if columns_map is not None:
        map_columns_names(columns_map, data)
    return data

def get_cells_from_df(data):
    try:
        cells = data[['e1', 'e2', 'e3']].dropna().astype('int').values
    except KeyError:
        raise KeyError('Columns e1, e2, and e3 must be present in the data set. Use'
                       'columns_map to map other names')
    return cells


def cells_from_delaunay(vertex):
    import pyvista as pv
    a = pv.PolyData(vertex)
    b = a.delaunay_2d().faces
    cells = b.reshape(-1, 4)[:, 1:]
    return cells


def get_vertices_from_df(data):
    try:
        vertex = data[['x', 'y', 'z']].values
    except KeyError:
        raise KeyError('Columns x, y, and z must be present in the data set. Use'
                       'columns_map to map other names')
    return vertex


def map_columns_names(columns_map: Union[Callable, dict, pd.Series], data: pd.DataFrame):
    data.columns = data.columns.map(columns_map)
    if data.columns.isin(['x', 'y', 'z']).any() is False:
        raise AttributeError('At least x, y, z must be passed to `columns_map`')

    return data.columns


def dxf_to_vertex_edges(file_or_buffer):
    vertex = dxf_to_vertex(file_or_buffer)
    tri = Delaunay(vertex[:, [0, 1]])
    faces = tri.simplices
    return faces, vertex


def dxf_to_vertex(file_or_buffer):
    import ezdxf
    dataset = ezdxf.readfile(file_or_buffer)
    vertex = []
    entity = dataset.modelspace()
    for e in entity:
        vertex.append(e[0])
        vertex.append(e[1])
        vertex.append(e[2])
    vertex = np.array(vertex)
    vertex = np.unique(vertex, axis=0)
    return vertex
