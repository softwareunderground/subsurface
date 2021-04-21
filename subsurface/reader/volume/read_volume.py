from subsurface.structs import UnstructuredData

from subsurface.reader.readers_data import ReaderFilesHelper
import pandas as pd


__all__ = ['read_volumetric_mesh_to_subsurface',
           'read_volumetric_mesh_coord_file',
           'read_volumetric_mesh_attr_file']


def read_volumetric_mesh_to_subsurface(reader_helper_coord: ReaderFilesHelper,
                                       reader_helper_attr: ReaderFilesHelper) -> UnstructuredData:
    df_coord = read_volumetric_mesh_coord_file(reader_helper_coord)
    df_attr = read_volumetric_mesh_attr_file(reader_helper_attr)
    combined_df = df_coord.merge(df_attr, left_index=True, right_index=True)
    ud = UnstructuredData.from_array(
        vertex=combined_df[['x', 'y', 'z']], cells="points",
        attributes=combined_df[['pres', 'temp', 'sg', 'xco2']]
    )
    return ud


def read_volumetric_mesh_coord_file(reader_helper: ReaderFilesHelper) -> pd.DataFrame:
    df = pd.read_csv(
        filepath_or_buffer=reader_helper.file_or_buffer, **reader_helper.pandas_reader_kwargs)
    if reader_helper.columns_map is not None: df.rename(reader_helper.columns_map,
                                                        axis="columns", inplace=True)
    df.dropna(axis=0, inplace=True)

    df.x = df.x.astype(float)
    df.y = df.y.astype(float)
    df.z = df.z.astype(float)
    return df


def read_volumetric_mesh_attr_file(reader_helper: ReaderFilesHelper) -> pd.DataFrame:
    df = pd.read_table(reader_helper.file_or_buffer, **reader_helper.pandas_reader_kwargs)
    df.columns = df.columns.str.strip()
    return df
