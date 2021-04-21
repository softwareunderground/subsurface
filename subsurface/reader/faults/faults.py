"""
TODO: This is legacy code waiting to be updated to the new ideas


"""

import pandas as pd


__all__ = ['read_faultsticks_kingdom', 'read_faultsticks_charisma']


def read_faultsticks_kingdom(fp: str, name=None):
    """
    Reads in Kingdom fault stick files (kingdom) exported from Petrel (tested
    with Petrel 2017) and returns pandas DataFrame.

    Args:
        fp (str): Filepath.
        name (str, optional): Default: None.

    Returns:
        (pandas.DataFrame) Fault stick information stored in dataframe with
        ["X", "Y", "Z", "formation", "stick id"] columns.

    """
    storage = []
    with open(fp, "r") as file:
        lines = file.readlines()
        for line in lines:
            line = line.split(" ")
            X = float(line[6])
            Y = float(line[7])
            Z = float(line[9])
            if name is None:
                name = line[10]
            else:
                name = name
            stick = int(line[-2])
            storage.append([X, Y, Z, name, stick])

    df = pd.DataFrame(storage)
    df.columns = ["X", "Y", "Z", "name", "stick id"]
    return df


def read_faultsticks_charisma(fp:str, name=None):
    """
    Reads in charisma fault stick files exported from Petrel (tested with
    Petrel 2017) and returns pandas DataFrame.

    Args:
        fp (str): Filepath.
        name (str, optional): Default: None.

    Returns:
        (pandas.DataFrame) Fault stick information stored in dataframe with
        ["X", "Y", "Z", "formation", "stick id"] columns.

    """
    storage = []
    with open(fp, "r") as file:  # due to the variable delimiter length its
                                 # easier to just manually read this in
        lines = file.readlines()
        for line in lines:
            line = line.split(" ")
            line = [l for l in line if len(l) >= 1]
            X = float(line[3])
            Y = float(line[4])
            Z = float(line[5])
            if name is None:
                name = line[6]
            else:
                name = name
            stick = int(line[-1])
            storage.append([X, Y, Z, name, stick])

    df = pd.DataFrame(storage)
    df.columns = ["X", "Y", "Z", "name", "stick id"]
    return df
