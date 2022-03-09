import subsurface
from subsurface import LineSet

from subsurface.reader.wells import WellyToSubsurfaceHelper, welly_to_subsurface


# TODO: Rename to test_read_from_las. I leave it like this to avoid calling it with the github actions. 
def _read_from_las():
    # There reading the code from las to welly
    # ...

    wts = WellyToSubsurfaceHelper()
    # wts.p += eachWell

    unstructured_data = welly_to_subsurface(wts)
    print('\n', unstructured_data)
    element = LineSet(unstructured_data)
    pyvista_mesh = subsurface.visualization.to_pyvista_line(element)

    # Plot default LITH
    subsurface.visualization.pv_plot([pyvista_mesh], image_2d=True)