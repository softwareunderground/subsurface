import enum
import numpy as np
import pandas as pd
import xarray as xr

from dataclasses import dataclass

from subsurface import UnstructuredData
from .collars import Collars
from .survey import Survey
from ...structs import LineSet
from ...structs.base_structures.base_structures_enum import SpecialCellCase


class MergeOptions(enum.Enum):
    RAISE = enum.auto()
    INTERSECT = enum.auto()
    

@dataclass
class BoreholeSet:
    collars: Collars
    survey: Survey
    combined_trajectory: LineSet
    
    def __Fooinit__(self, collars: Collars, survey: Survey, merge_option: MergeOptions = MergeOptions.RAISE):
        # check if they have the same ids and if not find the ones that are not in common
        collars_ids: list[str] = collars.ids
        survey_ids: list[str] = survey.ids

        diff_collars = list(set(collars_ids) - set(survey_ids))
        match merge_option:
            case MergeOptions.RAISE if collars_ids != survey_ids:
                raise ValueError(f"Collars and survey ids are not the same. Missing ids: {diff_collars}")
            case MergeOptions.INTERSECT:
                pass
                
        # Remove the ids that are not common in collars
        collards_ids_missing_idx = [collars_ids.index(d) for d in diff_collars]
        vertex: np.ndarray = collars.collar_loc.points
        
        # Remove the missing ids
        collar_loc = np.delete(vertex, collards_ids_missing_idx, axis=0)
        
        # remove vertex from survey that are not in common
        vertex_attr: pd.DataFrame = survey.survey_trajectory.data.points_attributes
        diff_survey = list(set(survey_ids) - set(collars_ids))
        survey_ids_missing_idx = [survey_ids.index(d) for d in diff_survey]
        
        # find the missing ids using the column "well_id"
        missing_ids = vertex_attr.loc[survey_ids_missing_idx, "well_id"]
        survey_trajectory_attr: pd.DataFrame  = vertex_attr.drop(index=missing_ids)
        
        # Drop the same rows in the survey vertext
        data_vertex: np.ndarray = survey.survey_trajectory.data.vertex
        survey_trajectory_vertex = np.delete(data_vertex, survey_ids_missing_idx, axis=0)
        
        # sum the collar_loc coordinates to each of the wells coordinates

    def __init__(self, collars, survey, merge_option):
        # Convert numpy arrays to DataFrames with well IDs as part of the DataFrame
        collar_df = pd.DataFrame(collars.collar_loc.points, columns=['X', 'Y', 'Z'])
        collar_df['well_id'] = collars.ids

        survey_df = pd.DataFrame(survey.survey_trajectory.data.vertex, columns=['X', 'Y', 'Z'])
        id_int = survey.survey_trajectory.data.points_attributes['well_id']
        id_str = id_int.map(pd.Series(survey.ids))
        survey_df['well_id'] = id_str

        # Merge data based on well IDs
        if merge_option == MergeOptions.RAISE:
            # Check for missing IDs in both directions
            missing_from_survey = set(collar_df['well_id']) - set(survey_df['well_id'])
            missing_from_collar = set(survey_df['well_id']) - set(collar_df['well_id'])
            if missing_from_survey or missing_from_collar:
                raise ValueError(f"Collars and survey ids do not match. Missing in survey: {missing_from_survey}, Missing in collars: {missing_from_collar}")

        elif merge_option == MergeOptions.INTERSECT:
            # Perform an inner join to only keep rows present in both DataFrames
            combined_df = pd.merge(collar_df, survey_df, on='well_id', suffixes=('_collar', '_survey'))

        # Adjust coordinates
        # Assuming we add the collar coordinates to each point of the survey trajectory
        combined_df['X_survey'] += combined_df['X_collar']
        combined_df['Y_survey'] += combined_df['Y_collar']
        combined_df['Z_survey'] += combined_df['Z_collar']

        # Now you can work with `combined_df` which has the adjusted coordinates.
        self.combined_data = combined_df
        
        combined_trajectory_unstruct = UnstructuredData.from_array(
            vertex=combined_df[['X_survey', 'Y_survey', 'Z_survey']].values,
            cells=SpecialCellCase.LINES,
            vertex_attr=combined_df[['well_id']]
        )
        
        self.combined_trajectory = LineSet(data=combined_trajectory_unstruct, radius=500)
        
        
        
    
        
