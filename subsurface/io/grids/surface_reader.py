import pandas as pd
from subsurface.structs.base_structures import UnstructuredData
import numpy as np
from scipy.spatial import Delaunay


def read_in_surface_vertices(path_to_file: str, delaunay: bool = True) -> UnstructuredData:
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

    print(data_cols)

    if np.array_equal(data_cols, ['x', 'y', 'z']):
        vertex = data.values
        # create edges with delaunay
        if delaunay is True:
            import pyvista as pv
            a = pv.PolyData(vertex)
            b = a.delaunay_2d().faces
            edges = b.reshape(-1, 4)[:, 1:]
        ud = UnstructuredData(vertex, edges)
        return ud

    elif np.array_equal(data_cols,['x', 'y', 'z', '0', '1', '2', '3']):
        vertex = np.asarray([x[:3] for x in data.values if not np.array_equiv(x[:3], ['nan', 'nan', 'nan'])])
        edges = np.asarray([x[3:] for x in data.values])
        ud = UnstructuredData(vertex, edges)
        return ud
