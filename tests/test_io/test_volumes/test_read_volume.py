import pathlib

from subsurface.reader.volume.volume_utils import interpolate_unstructured_data_to_structured_data
from subsurface.structs import PointSet, StructuredGrid

from subsurface.reader.readers_data import ReaderFilesHelper
from subsurface.reader.volume.read_volume import read_volumetric_mesh_coord_file, read_volumetric_mesh_attr_file, \
    read_volumetric_mesh_to_subsurface
from subsurface.visualization import to_pyvista_points, pv_plot, to_pyvista_grid

pf = pathlib.Path(__file__).parent.absolute()
data_path = pf.joinpath('../data/volume/')


def test_volumetric_mesh_to_subsurface():
    ud = read_volumetric_mesh_to_subsurface(
        ReaderFilesHelper(
            data_path.joinpath('mesh'),
            header=None,
            index_col=False,
            col_names=['elem', '_2', '_3', 'x', 'y', 'z'],
            additional_reader_kwargs={
                "skiprows": 1,
                "delimiter": "\s{2,}",
                "error_bad_lines": False,
                "nrows": None,
            }
        ),
        ReaderFilesHelper(
            data_path.joinpath('out_all00'),
            index_col=False,
            additional_reader_kwargs={"sep": ","}
        )
    )
    ps = PointSet(ud)
    mesh = to_pyvista_points(ps)
    pv_plot([mesh], image_2d=True)
    return ud, mesh


def test_interpolate_ud_to_sd():
    ud, ud_mesh = test_volumetric_mesh_to_subsurface()
    sd = interpolate_unstructured_data_to_structured_data(ud, "pres", [50, 50, 50])
    sg = StructuredGrid(sd)

    mesh = to_pyvista_grid(sg)
    pv_plot([mesh, ud_mesh], image_2d=True)


def test_read_volumetric_mesh():
    vol_mesh_coord_df = read_volumetric_mesh_coord_file(
        ReaderFilesHelper(
            data_path.joinpath('mesh'),
            header=None,
            index_col=False,
            col_names=['elem', '_2', '_3', 'x', 'y', 'z'],
            additional_reader_kwargs={
                "skiprows": 1,
                "delimiter": "\s{2,}",
                "error_bad_lines": False,
                "nrows": None,
            }
        )
    )

    print(vol_mesh_coord_df)

    vol_mesh_attr_df = read_volumetric_mesh_attr_file(
        ReaderFilesHelper(
            data_path.joinpath('out_all00'),
            index_col=False,
            additional_reader_kwargs={"sep": ","}
        )
    )

    print(vol_mesh_attr_df)
