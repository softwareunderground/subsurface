import pandas as pd
from dataclasses import dataclass

from ...structs.base_structures import UnstructuredData
from ...structs.base_structures.base_structures_enum import SpecialCellCase
from ...structs.unstructured_elements import PointSet


@dataclass
class Collars:
    ids: list[str]
    collar_loc: PointSet
    
    @classmethod
    def from_df(cls, df: pd.DataFrame):
        unstruc: UnstructuredData = UnstructuredData.from_array(
            vertex=df[["x", "y", "z"]].values,
            cells=SpecialCellCase.POINTS
        )
        return cls(
            ids=df.index.to_list(),
            collar_loc=PointSet(data=unstruc)
        )