import subsurface
from subsurface import LineSet
from subsurface.reader.wells import WellyToSubsurfaceHelper, welly_to_subsurface
from subsurface.reader.wells.welly_reader import create_welly_well_from_las


def test_read_from_las():
    address = r"C:\Users\legui\OneDrive - Terranigma Solutions GmbH\Documents\Products and Services\LiquidEarth\Test Data Sets\ET\ET Boreholes\LAS_TEST/"

    well = create_welly_well_from_las('Cottessen', address)

    wts = WellyToSubsurfaceHelper()
    wts.p += well

    unstructured_data = welly_to_subsurface(wts, convert_lith=False)
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)

    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=False)
