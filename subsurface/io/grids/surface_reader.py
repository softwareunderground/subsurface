import pandas as pd
from subsurface.structs.base_structures import UnstructuredData
import numpy as np
import math

from subsurface.structs.errors import VertexMissingError


def read_in_surface_vertices(path_to_file: str,
                             #  vertex_cols,
                             #  edge_cols=None,
                             columns_map: dict = None,
                             attribute_cols: dict = None,
                             delaunay: bool = True,
                             **kwargs) -> UnstructuredData:
    """
    Reads in csv files with n table columns and returns UnstructuredData object. m edges have to be in m columns named
    with the order of the points. If no edges are present default ones are generated.

    Vertex will be read from columns named x, y, z and edges from e1, e2, e3. You can use columns_map to map the required
    column names to any other name.

    Args:
        path_to_file (str): Filepath.
        columns_map (dict): Dictionary with format: {'csv_columns_name1': 'x', 'csv_columns_name2': 'y', ...}
        edge_cols (np.array (int)): m-element array with the indices of the columns where the edges are saved.
        vertex_cols (array-like (str,int)): s-element array with the indices of the columns where the vertices are saved
        attribute_cols (dict ()): t-element dict with the column names as keys and the column indices as the values
        delaunay (bool): If True compute edges using vtk Dalauny algorithm.
        kwargs: `pandas.read_csv` kwargs
    Returns:
        (UnstructuredData) csv with n columns stored in pandas.DataFrame of vertices with
        3 columns (3d vertices), edges of m columns forming an m-sided polygon and pandas.DataFrame of attributes with n-(m+3) columns.

    """
    # create dataframe
    data = pd.read_csv(path_to_file, **kwargs)
    # access columns
    data_cols = data.columns
    if columns_map is not None:
        data.columns = data.columns.map(columns_map)
        assert data.columns.isin(['x', 'y', 'z']).any(), 'At least x, y, z must be passed to `columns_map`'

    try:
        vertex = data[['x', 'y', 'z']].values
    except KeyError:
        raise KeyError('Columns x, y, and z must be present in the data set. Use'
                       'vertex_cols to map other names')
    try:
        edges = data[['e1', 'e2', 'e3']].dropna().astype('int').values
    except KeyError:
        if delaunay is True:
            import pyvista as pv
            a = pv.PolyData(vertex)
            b = a.delaunay_2d().faces
            edges = b.reshape(-1, 4)[:, 1:]
        else:
            raise AttributeError('Edges must be provided or computed by delaunay')

    # if len(vertex_cols) == 0:
    #     raise VertexMissingError
    # else:
    #     vertex = np.array([[x[y] for y in vertex_cols if not np.isnan(x[y])] for x in data.values])

    # if not edge_cols:
    #     # create edges with delaunay
    #     if delaunay is True:
    #         import pyvista as pv
    #         a = pv.PolyData(vertex)
    #         b = a.delaunay_2d().faces
    #         edges = b.reshape(-1, 4)[:, 1:]
    #     else:
    #         raise AttributeError('Edges must be provided or computed by delaunay')
    # else:
    #     # vertex = np.array([[x[y] for y in vertex_cols if not np.isnan(x[y])] for x in data.values])
    #     # print(vertex)
    #     edges = np.array([[int(x[y]) for y in edge_cols] for x in data.values
    #                       if not any(filter(math.isnan, [x[y] for y in edge_cols]))])

    ud = UnstructuredData(vertex, edges)

    print(edges)

    if attribute_cols:
        attributes = [[x[v] for k, v in attribute_cols.items()] for x in data.values]
        # print(len(attributes))
        df = pd.DataFrame(attributes)
        df.columns = [k for k, v in attribute_cols.items()]
        ud = UnstructuredData(vertex, edges, df)

    return ud
