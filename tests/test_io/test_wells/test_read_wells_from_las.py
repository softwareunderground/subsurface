import os

import pytest
import numpy as np
import pandas as pd
import subsurface
from conftest import RequirementsLevel
from subsurface import LineSet
from subsurface.reader import ReaderFilesHelper
from subsurface.reader.wells import WellyToSubsurfaceHelper, read_survey_df_from_las, read_assay_df_from_las, welly_to_subsurface


@pytest.mark.skipif(
    condition=(RequirementsLevel.WELLS | RequirementsLevel.BASE) not in RequirementsLevel.REQUIREMENT_LEVEL_TO_TEST(),
    reason="Need to set the READ_WELL variable to run this test"
)
def test_read_from_las():
    address = os.getenv("PATH_TO_COTTESSEN")
    if address is None:
        pytest.skip("No path to Cottessen las file")

    collar_coord = np.array([[707385, 5627164, 0]])
    collar_df = pd.DataFrame(index=["Cottessen"], data=collar_coord, columns=["X", "Y", "Z"])

    survey_reader = ReaderFilesHelper(
        file_or_buffer=address,
        usecols=["DEPT", "IMG_AZ", "IMG_INCL"],
        columns_map={"DEPT": "md", "IMG_AZ": "azi", "IMG_INCL": "inc"},
    )

    survey_df = read_survey_df_from_las(survey_reader, "Cottessen")
    assay_df = read_assay_df_from_las(ReaderFilesHelper(address), "Cottessen")
    
    wts = WellyToSubsurfaceHelper()
    wts.add_collar(collar_df)
    wts.add_deviation(survey_df)
    wts.add_assays(assay_df, "DEPT")

    unstructured_data = welly_to_subsurface(wts, convert_lith=False)
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=False)

