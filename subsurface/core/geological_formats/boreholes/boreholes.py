import enum
import numpy as np
import pandas as pd

from dataclasses import dataclass

from subsurface import UnstructuredData
from .collars import Collars
from .survey import Survey
from ...structs import LineSet


class MergeOptions(enum.Enum):
    RAISE = enum.auto()
    INTERSECT = enum.auto()


@dataclass
class BoreholeSet:
    collars: Collars
    survey: Survey
    combined_trajectory: LineSet

    def __init__(self, collars, survey, merge_option, slice_=slice(None)):
        # Convert numpy arrays to DataFrames with well IDs as part of the DataFrame

        collar_df = pd.DataFrame(collars.collar_loc.points[slice_], columns=['X', 'Y', 'Z'])
        collar_df['well_id'] = collars.ids[slice_]

        survey_df_vertex = pd.DataFrame(survey.survey_trajectory.data.vertex, columns=['X', 'Y', 'Z'])
        id_int_vertex = survey.survey_trajectory.data.points_attributes['well_id']
        survey_df_vertex['well_id'] = id_int_vertex.map(pd.Series(survey.ids))

        # Merge data based on well IDs
        if merge_option == MergeOptions.RAISE:  # Check for missing IDs in both directions
            missing_from_survey = set(collar_df['well_id']) - set(survey_df_vertex['well_id'])
            missing_from_collar = set(survey_df_vertex['well_id']) - set(collar_df['well_id'])
            if missing_from_survey or missing_from_collar:
                raise ValueError(f"Collars and survey ids do not match. Missing in survey: {missing_from_survey}, Missing in collars: {missing_from_collar}")

        elif merge_option == MergeOptions.INTERSECT:
            combined_df_vertex = pd.merge(collar_df, survey_df_vertex, on='well_id', suffixes=('_collar', '_survey'))  # Perform an inner join to only keep rows present in both DataFrames

            # Adjust coordinates
            # Assuming we add the collar coordinates to each point of the survey trajectory
            combined_df_vertex['X_survey'] += combined_df_vertex['X_collar']
            combined_df_vertex['Y_survey'] += combined_df_vertex['Y_collar']
            combined_df_vertex['Z_survey'] += combined_df_vertex['Z_collar']

            combined_df_cells = []  # Create a DataFrame for the cells
            previous_index = 0
            for e, well_id in enumerate(combined_df_vertex['well_id'].unique()):  # For each unique well_id in the combined_df_vertex DataFrame
                df_vertex_well = combined_df_vertex[combined_df_vertex['well_id'] == well_id]  # Filter the DataFrame for the current well_id 
                indices = np.arange(len(df_vertex_well)) + previous_index  # Create a range of indices for the current well
                previous_index += len(df_vertex_well)
                cells = np.array([indices[:-1], indices[1:]]).T  # Create the cells by pairing each index with the next one
                df_cells_well = pd.DataFrame(cells, columns=['cell1', 'cell2'])  # Create a DataFrame for the cells of the current well
                df_cells_well['well_id'] = well_id  # Add the well_id to the DataFrame
                df_cells_well['well_id_int'] = e

                combined_df_cells.append(df_cells_well)  # Append the DataFrame to the combined_df_cells DataFrame

            combined_df_cells = pd.concat(combined_df_cells, ignore_index=True)

            combined_trajectory_unstruct = UnstructuredData.from_array(
                vertex=combined_df_vertex[['X_survey', 'Y_survey', 'Z_survey']].values,
                cells=combined_df_cells[['cell1', 'cell2']].values,
                vertex_attr=survey.survey_trajectory.data.points_attributes,
                cells_attr=survey.survey_trajectory.data.cell_attributes
            )

            self.combined_trajectory = LineSet(data=combined_trajectory_unstruct, radius=500)
