import pathlib
from typing import TextIO, Union

import numpy as np

from subsurface import optional_requirements


def dxf_from_file_to_vertex(file_path: str):
    ezdxf = optional_requirements.require_ezdxf()
    dataset = ezdxf.readfile(file_path)
    vertex = []
    entity = dataset.modelspace()
    for e in entity:
        vertex.append(e[0])
        vertex.append(e[1])
        vertex.append(e[2])
    vertex = np.array(vertex)
    vertex = np.unique(vertex, axis=0)
    return vertex


def dxf_from_stream_to_vertex(stream: TextIO):
    ezdxf = optional_requirements.require_ezdxf()
    dataset = ezdxf.read(stream)
    vertex = []
    entity = dataset.modelspace()
    for e in entity:
        vertex.append(e[0])
        vertex.append(e[1])
        vertex.append(e[2])
    vertex = np.array(vertex)
    vertex = np.unique(vertex, axis=0)
    return vertex


def dxf_file_to_unstruct_input(file: Union[str, pathlib.Path]):
    ezdxf = optional_requirements.require_ezdxf()
    dataset = ezdxf.readfile(file)
    cell_attr_int, cell_attr_map, cells, vertex = _dxf_dataset_to_unstruct_input(dataset)

    return vertex, cells, cell_attr_int, cell_attr_map


def dxf_stream_to_unstruct_input(stream: TextIO):
    ezdxf = optional_requirements.require_ezdxf()
    dataset = ezdxf.read(stream)
    cell_attr_int, cell_attr_map, cells, vertex = _dxf_dataset_to_unstruct_input(dataset)

    return vertex, cells, cell_attr_int, cell_attr_map


def _dxf_dataset_to_unstruct_input(dataset):
    vertex = []
    cell_attr = []
    entity = dataset.modelspace()
    for e in entity:
        vertex.append(e[0])
        vertex.append(e[1])
        vertex.append(e[2])
        cell_attr.append(e.dxf.get("layer"))
    vertex = np.array(vertex)
    cells = np.arange(0, vertex.shape[0]).reshape(-1, 3)
    cell_attr_int, cell_attr_map = _map_cell_attr_strings_to_integers(cell_attr)
    return cell_attr_int, cell_attr_map, cells, vertex


def _map_cell_attr_strings_to_integers(cell_attr):
    d = dict([(y, x + 1) for x, y in enumerate(sorted(set(np.unique(cell_attr))))])
    cell_attr_int = np.array([d[x] for x in cell_attr])
    return cell_attr_int, d
