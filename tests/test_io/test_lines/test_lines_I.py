import os

import dotenv

from subsurface import UnstructuredData
from subsurface.core.geological_formats.boreholes.collars import Collars
from subsurface.core.reader_helpers.readers_data import GenericReaderFilesHelper
from subsurface.core.structs.base_structures.base_structures_enum import SpecialCellCase
from subsurface.core.structs.unstructured_elements import PointSet
from subsurface.modules.reader.wells.read_borehole_interface import read_collar

dotenv.load_dotenv()


def test_read_collar():
    reader: GenericReaderFilesHelper = GenericReaderFilesHelper(
        file_or_buffer=os.getenv("PATH_TO_SPREMBERG"),
        header=0,
        usecols=[0, 1, 2, 4],
        columns_map={
                "hole_id": "id", # ? Index name is not mapped
                "X_GK5_incl_inserted": "x",
                "Y__incl_inserted": "y",
                "Z_GK": "z"
        }
    )
    df = read_collar(reader)
    
    # TODO: df to unstruct
    unstruc: UnstructuredData = UnstructuredData.from_array(
        vertex= df[["x", "y", "z"]].values,
        cells= SpecialCellCase.POINTS
    )
    
    points = PointSet(data=unstruc)
    
    collars = Collars(
        ids=df.index.to_list(),
        collar_loc=points
    )
    
    pass
