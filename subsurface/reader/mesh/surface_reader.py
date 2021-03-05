import pandas as pd
from subsurface.structs.base_structures import UnstructuredData
from subsurface.utils.utils_core import get_extension
import numpy as np
from scipy.spatial.qhull import Delaunay


def read_2d_mesh(path_to_file: str,
                 columns_map: dict = None,
                 attribute_cols: dict = None,
                 delaunay: bool = True,
                 **reader_kwargs) -> UnstructuredData:
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
        reader_kwargs: `pandas.read_csv` kwargs
    Returns:
        (UnstructuredData) csv with n columns stored in pandas.DataFrame of vertices with
        3 columns (3d vertices), cells of m columns forming an m-sided polygon and pandas.DataFrame of attributes with n-(m+3) columns.

    """
    extension = get_extension(path_to_file)
    attr_dicts = dict()

    if extension == '.csv':
        attr_dicts, cells, vertex = csv_to_unstruct_args(attr_dicts, attribute_cols,
                                                         columns_map, delaunay,
                                                         path_to_file, reader_kwargs)
    elif extension == '.dxf':
        cells, vertex = dxf_to_vertex_edges(path_to_file)

    else:
        raise NotImplementedError('The extension given cannot be read yet')

    ud = UnstructuredData.from_array(vertex, cells, **attr_dicts)
    return ud


def csv_to_unstruct_args(attr_dicts, attribute_cols, columns_map, delaunay,
                         path_to_file, reader_kwargs):
    # create dataframe
    data = pd.read_csv(path_to_file, **reader_kwargs)
    if columns_map is not None:
        map_columns_names(columns_map, data)
    vertex = get_vertices_from_df(data)
    cells = get_cells_from_df(data, delaunay, vertex)
    if attribute_cols:
        attr_dicts = get_attributes_from_df(attribute_cols, cells, data, vertex)
    return attr_dicts, cells, vertex


def get_attributes_from_df(attribute_cols, cells, data, vertex):
    attributes = [[x[v] for k, v in attribute_cols.items()] for x in data.values]
    df = pd.DataFrame(attributes)
    df.columns = [k for k, v in attribute_cols.items()]
    # Check if is point or cell data
    if df.shape[0] == vertex.shape[0]:
        kwargs_ = {'points_attributes': df}
    elif df.shape[0] == cells.shape[0]:
        kwargs_ = {'attributes': df}
    else:
        raise ValueError(
            'Attribute cols must be either of the shape of vertex or'
            'cells.')
    return kwargs_


def get_cells_from_df(data, delaunay, vertex):
    try:
        cells = data[['e1', 'e2', 'e3']].dropna().astype('int').values
    except KeyError:
        if delaunay is True:
            import pyvista as pv
            a = pv.PolyData(vertex)
            b = a.delaunay_2d().faces
            cells = b.reshape(-1, 4)[:, 1:]
        else:
            raise AttributeError('cells must be provided or computed by delaunay')
    return cells


def get_vertices_from_df(data):
    try:
        vertex = data[['x', 'y', 'z']].values
    except KeyError:
        raise KeyError('Columns x, y, and z must be present in the data set. Use'
                       'columns_map to map other names')
    return vertex


def map_columns_names(columns_map, data):
    data.columns = data.columns.map(columns_map)
    if data.columns.isin(['x', 'y', 'z']).any() is False:
        raise AttributeError('At least x, y, z must be passed to `columns_map`')

    return data.columns


def dxf_to_vertex_edges(path):
    import ezdxf

    dataset = ezdxf.readfile(path)
    vertex = []
    entity = dataset.modelspace()
    for e in entity:
        vertex.append(e[0])
        vertex.append(e[1])
        vertex.append(e[2])
    vertex = np.array(vertex)
    vertex = np.unique(vertex, axis=0)
    tri = Delaunay(vertex[:, [0, 1]])
    faces = tri.simplices
    return faces, vertex