import dotenv
import os
import pandas as pd

from subsurface import UnstructuredData
from subsurface.core.geological_formats.boreholes.boreholes import BoreholeSet, MergeOptions
from subsurface.core.geological_formats.boreholes.collars import Collars
from subsurface.core.geological_formats.boreholes.survey import Survey
from subsurface.core.reader_helpers.readers_data import GenericReaderFilesHelper
from subsurface.core.structs.base_structures.base_structures_enum import SpecialCellCase
from subsurface.core.structs.unstructured_elements import PointSet
from subsurface.modules.reader.wells.read_borehole_interface import read_collar, read_survey, read_lith
from subsurface.modules.visualization import to_pyvista_points, pv_plot, to_pyvista_line

dotenv.load_dotenv()

PLOT = True


def test_read_collar():
    reader: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG_COLLAR"),
        header=0,
        usecols=[0, 1, 2, 4],
        columns_map={
                "hole_id"            : "id",  # ? Index name is not mapped
                "X_GK5_incl_inserted": "x",
                "Y__incl_inserted"   : "y",
                "Z_GK"               : "z"
        }
    )
    df = read_collar(reader)

    # TODO: df to unstruct
    unstruc: UnstructuredData = UnstructuredData.from_array(
        vertex=df[["x", "y", "z"]].values,
        cells=SpecialCellCase.POINTS
    )

    points = PointSet(data=unstruc)

    collars = Collars(
        ids=df.index.to_list(),
        collar_loc=points
    )

    if PLOT:
        s = to_pyvista_points(collars.collar_loc)
        pv_plot([s], image_2d=True)


def test_read_survey():
    reader: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG_SURVEY"),
        columns_map={
                'depth'  : 'md',
                'dip'    : 'dip',
                'azimuth': 'azi'
        },
    )
    df = read_survey(reader)

    survey: Survey = Survey.from_df(df)

    if PLOT and False:
        s = to_pyvista_line(
            line_set=survey.survey_trajectory,
            radius=10,
            active_scalar="well_id"
        )
        pv_plot([s], image_2d=False)

    return survey


def test_add_auxiliary_fields_to_survey():
    # TODO: Update this test to account for the ids mapping of assey or lith
    reader: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG_SURVEY"),
        columns_map={
                'depth'  : 'md',
                'dip'    : 'dip',
                'azimuth': 'azi'
        },
    )
    survey: Survey = Survey.from_df(read_survey(reader))
    import xarray as xr
    data_array: UnstructuredData = survey.survey_trajectory.data
    data_set: xr.Dataset = data_array.data

    pass


def test_read_stratigraphy():
    reader: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG_STRATIGRAPHY"),
        columns_map={
                'hole_id'   : 'id',
                'depth_from': 'top',
                'depth_to'  : 'base',
                'lit_code'  : 'component lith'
        }
    )

    lith: pd.DataFrame = read_lith(reader)
    survey: Survey = test_read_survey()

    survey.update_survey_with_lith(lith)

    reader_collar: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG_COLLAR"),
        header=0,
        usecols=[0, 1, 2, 4],
        columns_map={
                "hole_id"            : "id",  # ? Index name is not mapped
                "X_GK5_incl_inserted": "x",
                "Y__incl_inserted"   : "y",
                "Z_GK"               : "z"
        }
    )
    df_collar = read_collar(reader_collar)
    collar = Collars.from_df(df_collar)

    borehole_set = BoreholeSet(
        collars=collar,
        survey=survey,
        merge_option=MergeOptions.INTERSECT
    )

    if PLOT and True:
        s = to_pyvista_line(
            line_set=borehole_set.combined_trajectory,
            active_scalar="lith_ids",
            radius=10
        )
        pv_plot(
            meshes=[s],
            image_2d=False,
            # discrete colormap for at least 32 lithologies
            cmap="tab20",
            add_mesh_kwargs=
            {
                    #'clim': [0, borehole_set.combined_trajectory.data.points_attributes['lith'].max()],
            }
        )


def test_merge_collar_survey():
    reader_collar: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG_COLLAR"),
        header=0,
        usecols=[0, 1, 2, 4],
        columns_map={
                "hole_id"            : "id",  # ? Index name is not mapped
                "X_GK5_incl_inserted": "x",
                "Y__incl_inserted"   : "y",
                "Z_GK"               : "z"
        }
    )
    df_collar = read_collar(reader_collar)
    collar = Collars.from_df(df_collar)

    reader_survey: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG_SURVEY"),
        columns_map={
                'depth'  : 'md',
                'dip'    : 'dip',
                'azimuth': 'azi'
        },
    )

    survey = Survey.from_df(read_survey(reader_survey))

    borehole_set = BoreholeSet(
        collars=collar,
        survey=survey,
        merge_option=MergeOptions.INTERSECT
    )

    if PLOT:
        s = to_pyvista_line(line_set=borehole_set.combined_trajectory, radius=50)
        pv_plot([s], image_2d=False)
