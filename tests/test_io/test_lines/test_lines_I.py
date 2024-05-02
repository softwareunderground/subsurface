import os

import dotenv

from subsurface import UnstructuredData, LineSet
from subsurface.core.geological_formats.boreholes.collars import Collars
from subsurface.core.reader_helpers.readers_data import GenericReaderFilesHelper
from subsurface.core.structs.base_structures.base_structures_enum import SpecialCellCase
from subsurface.core.structs.unstructured_elements import PointSet
from subsurface.modules.reader.wells.read_borehole_interface import read_collar, read_survey
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


def test_read_assay():
    reader: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG_SURVEY"),
        columns_map={
                'depth'  : 'md',
                'dip'    : 'inc',
                'azimuth': 'azi'
        },
    )
    df = read_survey(reader)
    # Correct inclination to be in between 0 and 180. The current values are -90
    
    def correct_inclination(inc):
        if -360 < inc < -180:
            return 180 + inc
        elif -180 < inc < 0:
            return -inc
        elif 360 > inc > 180:
            return inc - 180
        else:
            raise ValueError(f'Inclination value {inc} is not in the range of 0 to 360')
        return inc
    
    df['inc'] = df['inc'].apply(correct_inclination)

    # split the dataframe by borehole id (index)
    # for each borehole, create a deviation object
    # add deviation object to well object

    import wellpathpy as wp
    import numpy as np
    for borehole_id, data in df.groupby(level=0):
        dev: wp.deviation = wp.deviation(
            md=data['md'],
            inc=data['inc'],
            azi=data['azi']
        )
        step = 30
        depths = list(range(0, int(dev.md[-1]) + 1, step))
        pos = dev.minimum_curvature().resample(depths=depths)

        break

    unstruct = UnstructuredData.from_array(
        vertex=np.vstack([pos.easting, pos.northing, pos.depth]).T,
        cells=SpecialCellCase.LINES
    )
    
    if PLOT:
        s = to_pyvista_line(line_set=LineSet(data=unstruct, radius=50))
        pv_plot([s], image_2d=False)

    pass
