import pandas as pd
from subsurface.structs.base_structures import UnstructuredData
import numpy as np
from scipy.spatial import Delaunay


def read_in_surface_vertices(path_to_file: str) -> UnstructuredData:
    """
    Reads in csv files with n columns and returns UnstructuredData object.

    Args:
        path_to_file (str): Filepath.

    Returns:
        (base_structures.UnstructuredData) csv with n columns stored in pandas.DataFrame of vertices with
        3 columns and pandas.DataFrame of attributes with n-3 columns.

    """
    # create dataframe
    data = pd.read_csv(path_to_file)
    # access columns
    data_cols = data.columns

    if (data_cols == ['x', 'y', 'z']).all():
        vertex = data.values
        # create edges with delaunay
        edges = Delaunay(data).vertex_to_simplex
        ud = UnstructuredData(vertex, edges)
        return ud
    else:
        if data_cols == ['x', 'y', 'z', 'edge']:
            pass
