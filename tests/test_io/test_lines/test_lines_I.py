import dotenv
import os

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

    if PLOT:
        s = to_pyvista_line(line_set=survey.survey_trajectory, radius=10)
        pv_plot([s], image_2d=False)
    
    return survey


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
    
    lith = read_lith(reader)
    survey = test_read_survey()
    pass


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
