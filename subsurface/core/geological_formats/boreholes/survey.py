import pandas as pd
from dataclasses import dataclass

from subsurface import optional_requirements
from ...structs.unstructured_elements import LineSet
from ...structs.base_structures import UnstructuredData

STEP = 30
RADIUS = 10


@dataclass
class Survey:
    ids: list[str]
    survey_trajectory: LineSet

    @classmethod
    def from_df(cls, df: 'pd.DataFrame'):
        trajectories: UnstructuredData = _data_frame_to_unstructured_data(
            df=_correct_angles(df)
        )
        # Grab the unique ids
        unique_ids = df.index.get_level_values(0).unique().tolist()
        
        return cls(
            ids=unique_ids,
            survey_trajectory=LineSet(data=trajectories, radius=RADIUS)
        )


def _correct_angles(df: pd.DataFrame) -> pd.DataFrame:
    def correct_inclination(inc: float) -> float:
        if inc < 0:
            inc = inc % 360  # Normalize to 0-360 range first if negative
        if 0 <= inc <= 180:
            return inc - 0.000001
        elif 180 < inc < 360:
            return 360 - inc  # Reflect angles greater than 180 back into the 0-180 range
        else:
            raise ValueError(f'Inclination value {inc} is out of the expected range of 0 to 360 degrees')

    def correct_azimuth(azi: float) -> float:
        return azi % 360  # Normalize azimuth to 0-360 range

    df['inc'] = df['inc'].apply(correct_inclination)
    df['azi'] = df['azi'].apply(correct_azimuth)

    return df



def _data_frame_to_unstructured_data(df: 'pd.DataFrame'):
    import numpy as np
    
    wp = optional_requirements.require_wellpathpy()
    pd = optional_requirements.require_pandas()
    
    vertex: np.ndarray = np.empty((0, 3), dtype=np.float_)
    cells: np.ndarray = np.empty((0, 2), dtype=np.int_)
    cell_attr: pd.DataFrame = pd.DataFrame(columns=['well_id'])
    vertex_attr: pd.DataFrame = pd.DataFrame(columns=['well_id'])

    for e, (borehole_id, data) in enumerate(df.groupby(level=0)):
        dev: wp.deviation = wp.deviation(
            md=data['md'],
            inc=data['inc'],
            azi=data['azi']
        )
        depths = list(range(0, int(dev.md[-1]) + 1, STEP))
        pos = dev.minimum_curvature().resample(depths=depths)
        vertex_count = vertex.shape[0]

        vertex = np.vstack([
                vertex,
                np.vstack([pos.easting, pos.northing, pos.depth]).T]
        )

        n_vertex_shift_0 = np.arange(0, len(pos.depth) - 1, dtype=np.int_)
        n_vertex_shift_1 = np.arange(1, len(pos.depth), dtype=np.int_)
        cell_per_well = np.vstack([n_vertex_shift_0, n_vertex_shift_1]).T + vertex_count
        cells = np.vstack([cells, cell_per_well], dtype=np.int_)
        
        # Add the id (e), to cell_attr and vertex_attr
        cell_attr = pd.concat([cell_attr, pd.DataFrame({'well_id': [e] * len(cell_per_well)})])
        vertex_attr = pd.concat([vertex_attr, pd.DataFrame({'well_id': [e] * len(pos.depth)})])

    unstruct = UnstructuredData.from_array(
        vertex=vertex,
        cells=cells,
        vertex_attr=vertex_attr.reset_index(),
        cells_attr=cell_attr.reset_index()
    )

    return unstruct
