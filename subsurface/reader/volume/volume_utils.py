from typing import List

from scipy.interpolate import griddata
import numpy as np

from subsurface.structs import UnstructuredData, StructuredData


__all__ = ['interpolate_unstructured_data_to_structured_data', ]


def interpolate_unstructured_data_to_structured_data(ud: UnstructuredData, attr_name: str,
                                                     resolution: List[int] = None) -> StructuredData:
    if resolution is None:
        resolution = [50, 50, 50]
    boundaries_max = ud.vertex.max(axis=0)
    boundaries_min = ud.vertex.min(axis=1)
    coords = dict()
    dims = ['x', 'y', 'z']
    for e, i in enumerate(dims):
        coords[i] = np.linspace(boundaries_min[e], boundaries_max[e], resolution[e], endpoint=False)

    grid = np.meshgrid(*coords.values())

    interpolated_attributes = griddata(ud.vertex,
                                       ud.attributes.loc[:, attr_name],
                                       tuple(grid), method='linear')

    sd = StructuredData.from_numpy(
        array=interpolated_attributes,
        data_array_name=attr_name,
        coords=coords
    )
    return sd
