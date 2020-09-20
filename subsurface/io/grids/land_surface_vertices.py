#from pandas_ods_reader import read_ods
import pandas as pd

def read_in_land_surface_vertices(path_to_file : str):
    """
    Reads in csv files with x, y, z coordinates and returns pandas DataFrame.

    Args:
        path_to_file (str): Filepath.

    Returns:
        (pandas.DataFrame) Vertices coordinates stored in dataframe with
        ["X", "Y", "Z"] columns.

    """

    storage = []

    with open(path_to_file, 'r') as fi:
        lines = fi.readlines()
        for line in lines[1:]:
            line = line.split(",")
            X = float(line[0])
            Y = float(line[1])
            Z = float(line[2])

            storage.append([X, Y, Z])

    df = pd.DataFrame(storage)
    df.columns = ['X', 'Y', 'Z']

    return df