from typing import Union, Hashable

import pandas as pd
from dataclasses import dataclass
import numpy as np
import xarray as xr

from subsurface import optional_requirements
from ...structs.unstructured_elements import LineSet
from ...structs.base_structures import UnstructuredData

STEP = 30
RADIUS = 10


@dataclass
class Survey:
    ids: list[str]
    survey_trajectory: LineSet
    well_id_mapper: dict[str, int] = None
    
    @classmethod
    def from_df(cls, df: 'pd.DataFrame'):
        trajectories: UnstructuredData = _data_frame_to_unstructured_data(
            df=_correct_angles(df)
        )
        # Grab the unique ids
        unique_ids = df.index.get_level_values(0).unique().tolist()
        
        # fill well_id_mapper
        well_id_mapper = {well_id: e for e, well_id in enumerate(unique_ids)}
        
        return cls(
            ids=unique_ids,
            survey_trajectory=LineSet(data=trajectories, radius=RADIUS),
            well_id_mapper=well_id_mapper
        )
    
    def get_well_string_id(self, well_id: int) -> str:
        return self.ids[well_id]
    
    def get_well_id(self, well_string_id: Union[str, Hashable]) -> int:
        return self.well_id_mapper.get(well_string_id, None)
    
    def update_survey_with_lith(self, lith: pd.DataFrame):
        arrays_dict = _combine_survey_and_lith(lith, self)
        self.survey_trajectory.data = arrays_dict
    
    
def __combine_survey_and_lith(lith: pd.DataFrame, survey: Survey) -> UnstructuredData:
    from ...structs.base_structures._unstructured_data_constructor import raw_attributes_to_dict_data_arrays
    
    trajectory: xr.DataArray = survey.survey_trajectory.data.data["vertex_attrs"]
    well_ids = trajectory.sel({'vertex_attr': 'well_id'})
    depths = trajectory.sel({'vertex_attr': 'depth'})
    bar = depths.values
    new_attrs = survey.survey_trajectory.data.points_attributes
    new_attrs['lith'] = np.zeros((trajectory.shape[0], 1), dtype=int)
    # Convert segment data to a form usable with xarray
    for index, row in lith.iterrows():
        well_id = survey.get_well_id(index)
        well_id_mask = well_ids == well_id
        spatial_mask = ((depths <= row['top']) & (depths >= row['base']))
        mask = well_id_mask & spatial_mask
        new_attrs.loc[mask.values, 'lith'] = row['component lith']
        
    labels, unique = pd.factorize(new_attrs['lith'])
    new_attrs['lith'] = labels
    points_attributes_xarray_dict: dict[str, xr.DataArray] = raw_attributes_to_dict_data_arrays(
        default_attributes_name="vertex_attrs",
        n_items=trajectory.shape[0],
        dims=["points", "vertex_attr"],
        raw_attributes=new_attrs
    )
    
    vertex_attrs_ = points_attributes_xarray_dict["vertex_attrs"]
    new_unstruct = UnstructuredData.from_data_arrays_dict(
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
    return new_unstruct


def _combine_survey_and_lith(lith: pd.DataFrame, survey: Survey) -> UnstructuredData:
    # Import moved to top for clarity and possibly avoiding repeated imports if called multiple times
    from ...structs.base_structures._unstructured_data_constructor import raw_attributes_to_dict_data_arrays

    # Accessing trajectory data more succinctly
    trajectory = survey.survey_trajectory.data.data["vertex_attrs"]
    well_ids = trajectory.sel({'vertex_attr': 'well_id'})
    depths = trajectory.sel({'vertex_attr': 'depth'})

    # Simplified creation of a new 'lith' attribute initialized to zeros
    # new_attrs = survey.survey_trajectory.data.points_attributes
    # new_attrs['lith'] = np.zeros(trajectory.shape[0], dtype=int)  # Changed shape for correct dimension

    new_attrs = survey.survey_trajectory.data.points_attributes
    new_attrs['lith'] = np.full(trajectory.shape[0], np.nan)  # Use np.nan and np.full for initialization

    for index, row in lith.iterrows():
        well_id = survey.get_well_id(index)
        well_id_mask = well_ids == well_id
        spatial_mask = ((depths <= row['top']) & (depths >= row['base']))
        mask = well_id_mask & spatial_mask
        new_attrs.loc[mask.values, 'lith'] = row['component lith']

    # Factorize lith components directly in-place
    new_attrs['lith'], _ = pd.factorize(new_attrs['lith'], use_na_sentinel=True)

    # Construct the final xarray dict without intermediate variable
    points_attributes_xarray_dict = raw_attributes_to_dict_data_arrays(
        default_attributes_name="vertex_attrs",
        n_items=trajectory.shape[0],
        dims=["points", "vertex_attr"],
        raw_attributes=new_attrs
    )

    # Inline construction of UnstructuredData
    return UnstructuredData.from_data_arrays_dict(
        xarray_dict={
                "vertex"      : survey.survey_trajectory.data.data["vertex"],
                "cells"       : survey.survey_trajectory.data.data["cells"],
                "vertex_attrs": points_attributes_xarray_dict["vertex_attrs"],
                "cell_attrs"  : survey.survey_trajectory.data.data["cell_attrs"]
        },
        xarray_attributes=survey.survey_trajectory.data.data.attrs,
        default_cells_attributes_name=survey.survey_trajectory.data.cells_attr_name,
        default_points_attributes_name=survey.survey_trajectory.data.vertex_attr_name
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
        pos: wp.minimum_curvature = dev.minimum_curvature().resample(depths=depths)
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
        vertex_attr = pd.concat([vertex_attr, pd.DataFrame(
            {
                    'well_id': [e] * len(pos.depth),
                    'depth': pos.depth,
             }
        )])

    unstruct = UnstructuredData.from_array(
        vertex=vertex,
        cells=cells,
        vertex_attr=vertex_attr.reset_index(),
        cells_attr=cell_attr.reset_index()
    )

    return unstruct
