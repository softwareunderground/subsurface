import pandas

import subsurface
from subsurface import LineSet
import numpy as np
import welly
import glob
import pandas as pd

from subsurface.reader.wells import WellyToSubsurfaceHelper, welly_to_subsurface


def create_well(uwi: str = 'dummy_uwi'):
    w = welly.Well()
    w.location.uwi = uwi

    return w


def read_curves_to_welly_object(well, curve_path: str = '.'):
    las_files = glob.glob(curve_path + '*.las')
    for curve in las_files:
        well.add_curves_from_las(curve)
    # return well


def welly_to_df(well):
    return well.df()


def make_deviation_df(well_df: pd.DataFrame, inclination_header: str, azimuth_header: str,
                      depth_header: str = '', depth_index=True):
    if depth_index:
        deviation_data = well_df[[inclination_header, azimuth_header]].to_numpy()
        deviation_index = well_df.index.to_numpy()
        deviation_complete = np.insert(deviation_data, 0, deviation_index, axis=1)
        deviation_complete = deviation_complete[~np.isnan(deviation_complete).any(axis=1), :]
    else:
        deviation_complete = well_df[[depth_header, inclination_header, azimuth_header]].to_numpy()
        deviation_complete = deviation_complete[~np.isnan(deviation_complete).any(axis=1), :]
    return deviation_complete
# TODO: Rename to test_read_from_las. I leave it like this to avoid calling it with the github actions. 
def test_read_from_las():
    w = create_well('Cottessen')
    read_curves_to_welly_object(w,
                                curve_path='C:\\Users\\Simon\\OneDrive - Terranigma Solutions GmbH\\Test Data Sets\\ET\\ET Boreholes/LAS_TEST/')

    # There reading the code from las to welly
    # ...
    w_df = welly_to_df(w)
    deviation_df = make_deviation_df(w_df, inclination_header='IMG_INCL', azimuth_header='IMG_AZ')
    w.location.add_deviation(deviation_df)

    wts = WellyToSubsurfaceHelper()
    wts.p += w
    #wts.add_deviation(deviation_df)


    unstructured_data = welly_to_subsurface(wts, convert_lith=False)
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)

    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=False)