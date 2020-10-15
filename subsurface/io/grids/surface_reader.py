import pandas as pd
from subsurface.structs.base_structures import UnstructuredData
import numpy as np
import math
from scipy.spatial import Delaunay

from subsurface.structs.errors import VertexMissingError


def read_in_surface_vertices(path_to_file: str, vertex_cols: np.array([int]), edge_cols: np.array([int]),
                             attribute_cols: dict = None,
                             delaunay: bool = True) -> UnstructuredData:
    """
    Reads in csv files with n table columns and returns UnstructuredData object. m edges have to be in m columns named
    with the order of the points. If no edges are present default ones are generated.

    Args:
        path_to_file (str): Filepath.
        edge_cols (np.array (int)): m-element array with the indices of the columns where the edges are saved.
        vertex_cols (np.array (int)): s-element array with the indices of the columns where the vertices are saved
        attribute_cols (dict ()): t-element dict with the column names as keys and the column indices as the values

    Returns:
        (UnstructuredData) csv with n columns stored in pandas.DataFrame of vertices with
        3 columns (3d vertices), edges of m columns forming an m-sided polygon and pandas.DataFrame of attributes with n-(m+3) columns.

    """
    # create dataframe
    data = pd.read_csv(path_to_file)
    # access columns
    data_cols = data.columns

    if len(vertex_cols) == 0:
        raise VertexMissingError
    else:
        vertex = np.array([[x[y] for y in vertex_cols if not np.isnan(x[y])] for x in data.values])

    if not edge_cols:
        # create edges with delaunay
        if delaunay is True:
            import pyvista as pv
            a = pv.PolyData(vertex)
            b = a.delaunay_2d().faces
            edges = b.reshape(-1, 4)[:, 1:]

    else:
        # vertex = np.array([[x[y] for y in vertex_cols if not np.isnan(x[y])] for x in data.values])
        # print(vertex)
        edges = np.array([[int(x[y]) for y in edge_cols] for x in data.values
                          if not any(filter(math.isnan, [x[y] for y in edge_cols]))])

    ud = UnstructuredData(vertex, edges)

    print(edges)

    if attribute_cols:
        attributes = [[x[v] for k, v in attribute_cols.items()] for x in data.values]
        # print(len(attributes))
        df = pd.DataFrame(attributes)
        df.columns = [k for k, v in attribute_cols.items()]
        ud = UnstructuredData(vertex, edges[:len(attributes)], df)

    return ud
