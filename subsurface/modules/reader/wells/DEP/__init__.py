def borehole_location_to_unstruct(reader_helper: ReaderFilesHelper,
                                  add_number_segments: bool = True) -> UnstructuredData:
    from . import _wells_api
    return _wells_api.borehole_location_to_unstruct(reader_helper, add_number_segments)


def read_survey_df_from_las(reader_helper: ReaderFilesHelper, well_name: str) -> 'pd.DataFrame':
    from .DEP import _well_files_reader
    return _well_files_reader.read_survey_df_from_las(reader_helper, well_name)


def read_assay_df_from_las(reader_helper: ReaderFilesHelper, well_name: str) -> 'pd.DataFrame':
    from .DEP import _well_files_reader
    return _well_files_reader.read_assay_df_from_las(reader_helper, well_name)


def welly_to_subsurface(wts: WellyToSubsurfaceHelper,
                        elev=True,
                        n_vertex_per_well=50,
                        convert_lith=True,
                        table: list['striplog.Component'] = None,
                        **kwargs) -> UnstructuredData:
    """Method to convert well data to `subsurface.UnstructuredData`

    Args:
        elev (bool): In general the (x, y, z) array of positions will have
            z as TVD, which is positive down. If `elev` is True, positive
            will be upwards.
        n_vertex_per_well (int): Number of vertex used to describe the geometry of the
         well.
        return_element (bool): if True return a `subsurface.LineSet` instead
        convert_lith (bool): if True convert lith from stiplog to curve
        table (List[Striplog.Component]): List of components to map lithologies
         to value.
        **kwargs:
            `Well.location.trajectory` kwargs

    Returns:

    """
    from . import _welly_reader
    return _welly_reader.welly_to_subsurface(wts, elev, n_vertex_per_well, convert_lith, table, **kwargs)

