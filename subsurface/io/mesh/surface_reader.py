import pandas as pd
from subsurface.structs.base_structures import UnstructuredData


def read_2d_mesh(path_to_file: str,
                 columns_map: dict = None,
                 attribute_cols: dict = None,
                 delaunay: bool = True,
                 **kwargs) -> UnstructuredData:
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
        kwargs: `pandas.read_csv` kwargs
    Returns:
        (UnstructuredData) csv with n columns stored in pandas.DataFrame of vertices with
        3 columns (3d vertices), cells of m columns forming an m-sided polygon and pandas.DataFrame of attributes with n-(m+3) columns.

    """
    # create dataframe
    data = pd.read_csv(path_to_file, **kwargs)

    if columns_map is not None:
        data.columns = data.columns.map(columns_map)
        assert data.columns.isin(['x', 'y', 'z']).any(), 'At least x, y, z must be passed to `columns_map`'

    try:
        vertex = data[['x', 'y', 'z']].values
    except KeyError:
        raise KeyError('Columns x, y, and z must be present in the data set. Use'
                       'vertex_cols to map other names')
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

    ud = UnstructuredData(vertex, cells)

    if attribute_cols:
        attributes = [[x[v] for k, v in attribute_cols.items()] for x in data.values]
        df = pd.DataFrame(attributes)
        df.columns = [k for k, v in attribute_cols.items()]

        # Check if is point or cell data
        if df.shape[0] == vertex.shape[0]:
            kwargs_ = {'points_attributes': df}
        elif df.shape[0] == cells.shape[0]:
            kwargs_ = {'attributes': df}
        else:
            raise ValueError('Attribute cols must be either of the shape of vertex or'
                             'cells.')

        ud = UnstructuredData(vertex, cells, **kwargs_)

    return ud
