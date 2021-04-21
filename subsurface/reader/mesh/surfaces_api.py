from subsurface.structs import UnstructuredData

from subsurface.reader.mesh.surface_reader import read_mesh_file_to_vertex, read_mesh_file_to_cells, \
    cells_from_delaunay, read_mesh_file_to_attr
from subsurface.reader.readers_data import ReaderUnstructuredHelper, RawDataOptions, RawDataUnstructured

__all__ = ['read_2d_mesh_to_unstruct', ]


def read_2d_mesh_to_unstruct(reader_args: ReaderUnstructuredHelper,
                             raw_data_options: RawDataOptions = None,
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
