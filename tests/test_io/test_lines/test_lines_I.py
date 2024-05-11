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

    lith = read_lith(reader)
    survey = test_read_survey()
    import xarray as xr
    import numpy as np
    trajectory: xr.DataArray = survey.survey_trajectory.data.data["vertex_attrs"]

    well_ids = trajectory.sel({'vertex_attr': 'well_id'})
    depths = trajectory.sel({'vertex_attr': 'depth'})
    bar = depths.values

    # new_attrs = pd.DataFrame(
    #     columns=['lith'], 
    #     data=np.zeros((trajectory.shape[0], 1), dtype=int)
    # )

    new_attrs = survey.survey_trajectory.data.points_attributes
    new_attrs['lith'] = np.zeros((trajectory.shape[0], 1), dtype=int)

    # Convert segment data to a form usable with xarray
    for index, row in lith.iterrows():
        well_id = survey.get_well_id(index)
        well_id_mask = well_ids == well_id
        spatial_mask = ((depths <= row['top']) & (depths >= row['base']))
        mask = well_id_mask & spatial_mask
        argwhere = np.argwhere(mask.values)
        # print(argwhere)
        new_attrs.loc[mask.values, 'lith'] = row['component lith']

    labels, unique = pd.factorize(new_attrs['lith'])
    new_attrs['lith'] = labels
    
    from subsurface.core.structs.base_structures._unstructured_data_constructor import raw_attributes_to_dict_data_arrays
    points_attributes_xarray_dict: dict[str, xr.DataArray] = raw_attributes_to_dict_data_arrays(
        default_attributes_name="vertex_attrs",
        n_items=trajectory.shape[0],
        dims=["points", "vertex_attr"],
        raw_attributes=new_attrs
    )

    vertex_attrs_ = points_attributes_xarray_dict["vertex_attrs"]
    arrays_dict = UnstructuredData.from_data_arrays_dict(
        xarray_dict={
                "vertex"      : survey.survey_trajectory.data.data["vertex"],
                "cells"       : survey.survey_trajectory.data.data["cells"],
                "vertex_attrs": vertex_attrs_,
                "cell_attrs"  : survey.survey_trajectory.data.data["cell_attrs"]
        },
        xarray_attributes=survey.survey_trajectory.data.data.attrs,
        default_cells_attributes_name=survey.survey_trajectory.data.cells_attr_name,
        default_points_attributes_name=survey.survey_trajectory.data.vertex_attr_name
    )
    survey.survey_trajectory.data = arrays_dict


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
            active_scalar="lith",
            radius=10
        )
        pv_plot(
            meshes=[s], 
            image_2d=False,
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
