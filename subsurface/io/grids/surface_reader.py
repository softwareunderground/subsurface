import pandas as pd
from subsurface.structs.unstructured_elements import PointSet
from subsurface.structs.base_structures import UnstructuredData


def read_in_surface_vertices(path_to_file: str):
    """
    Reads in csv files with n columns and returns pandas DataFrame.

    Args:
        path_to_file (str): Filepath.

    Returns:
        (pandas.DataFrame) Vertices coordinates stored in dataframe with
        n columns.

    """
    # create dataframe
    data = pd.read_csv(path_to_file)

    # access columns
    data_cols = data.columns

    if data_cols == ['x', 'y', 'z']:
        ps: PointSet
        ps.vertex = data
        return ps
    else:
        if data_cols == ['x', 'y', 'z', 'edge']: # check format of edges for creating the right Unstructured data object
            ps.vertex = data
            ps.edges

    # how can we find out if csv includes edges?

    # with open(path_to_file, 'r') as fi:
    #     lines = fi.readlines()
    #     for line in lines[1:]:
    #         line = line.split(",")
    #         X = float(line[0])
    #         Y = float(line[1])
    #         Z = float(line[2])
    #
    #         storage.append([X, Y, Z])
    #
    # df = pd.DataFrame(storage)
    # df.columns = ['X', 'Y', 'Z']
    #
    # return df