import pandas as pd
from dataclasses import dataclass

from ...structs.unstructured_elements import UnstructuredData


@dataclass
class Collars:
    ids: list[str]
    collar_loc: UnstructuredData
    
    @classmethod
    def from_df(cls, df: pd.DataFrame):
        return cls(
            ids=df.index.to_list(),
            collar_loc=UnstructuredData.from_array(
                vertex=df[['x', 'y', 'z']]),
            cells=""
            
        )