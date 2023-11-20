import json

import numpy as np
import xarray as xr


def read_data(json_file_path, binary_file_path):
    header = _read_json_header(json_file_path)
    data_dict = _read_binary_data(binary_file_path, header)
    return data_dict, header


def _read_json_header(json_file_path):
    with open(json_file_path, 'r') as f:
        header = json.load(f)
    return header


def _read_binary_data(binary_file_path, header, order='F'):
    # Initialize offset to 0
    offset = 0
    # Create a dictionary to hold the arrays
    data_dict = {}

    # Loop over the arrays
    for array_name in ['vertex', 'cell', 'cell_attr', 'vertex_attr']:
        # Get the shape and type of the array from the header
        array_shape = header.get(f'{array_name}_shape')
        array_type = header.get(f'{array_name}_types', 'float32')  # default to float32 if not found

        # Calculate the number of elements in the array
        num_elements = np.prod(array_shape)

        # Read the data
        data = np.fromfile(binary_file_path, dtype="int32", count=num_elements, offset=offset)
        data = data.reshape(array_shape, order=order)

        # Store the data in the dictionary
        data_dict[array_name] = data

        # Update the offset
        offset += data.nbytes

    return data_dict


