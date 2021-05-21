import pytest

import subsurface
from subsurface.interfaces.liquid_earth.rest_client import LiquidEarthClient, DataTypes
from subsurface.reader.read_netcdf import read_unstruct, read_struct

from subsurface.reader.mesh.surface_reader import dxf_to_mesh
import trimesh
import numpy as np
import pandas


@pytest.mark.skip(reason="This functionality is under development and it is supposed to be trigger"
                         "only manually.")
class TestLiquidEarthClient:

    @pytest.fixture(scope="module")
    def liquid_earth_client(self):
        c = LiquidEarthClient()
        c.login(
            "yourUser", # TODO: Add your LiquidEarth Credentials here!
            "yourPassword"
        )
        return c

    def test_upload_data_to_new_project(self, liquid_earth_client, data_path):
        liquid_earth_client.add_new_project(
            "Shafts",
            project_id="museum",
            extent=[5.87907467e+05, 5.88328512e+05, 6.64175515e+06, 6.64232280e+06, -2.45600098e+02,
                    7.30000000e+01]
        )

        unstruc = self.test_dataset2(data_path)

        body, header = unstruc.to_binary()

        liquid_earth_client.add_data_to_project(
            project_id="museum",
            data_name="shafts_meshes",
            data_type=DataTypes.static_mesh,
            header=header,
            body=body
        )

    def test_get_valid_token(self):
        client = LiquidEarthClient()
        client.login("miguel@terranigma-solutions.com", "demoaccount")

    def test_get_available_projects(self, liquid_earth_client):
        liquid_earth_client.get_available_projects()

    def test_add_new_project(self, liquid_earth_client):
        liquid_earth_client.add_new_project(
            "subsurface_project",
            project_id="52f88baa-c84c-4082-bbba-869ef3819004",
            extent=[0, 10, -10, 0, 0, 10]
        )

    def test_add_data_to_project(self, liquid_earth_client, data_path):
        us = read_unstruct(data_path + '/interpolator_meshes.nc')
        print(us.extent)
        body, header = us.to_binary()

        liquid_earth_client.add_data_to_project(
            project_id="52f88baa-c84c-4082-bbba-869ef3819004",
            data_name="data_from_subsurface",
            data_type=DataTypes.static_mesh,
            header=header,
            body=body
        )

    def test_update_meta_data(self, liquid_earth_client):
        liquid_earth_client._post_update_meta_data(
            project_id="52f88baa-c84c-4082-bbba-869ef3819004",
            data_name="data_from_subsurface.le",
            data_type=DataTypes.static_mesh
        )

        return

    def test_dataset1(self, data_path):
        us = read_unstruct(data_path + '/interpolator_meshes.nc')

    def test_dataset2(self, data_path):
        path = data_path + '/surfaces/shafts.dxf'

        vertex, cells, cell_attr_int, cell_attr_map = dxf_to_mesh(path)

        tri = trimesh.Trimesh(vertex, faces=cells)

        unstruct = subsurface.UnstructuredData.from_array(
            np.array(tri.vertices),
            np.array(tri.faces),
            cells_attr=pandas.DataFrame(cell_attr_int, columns=["Shaft id"]),
            xarray_attributes={"bounds": tri.bounds.tolist(),
                               "cell_attr_map": cell_attr_map
                               },
        )

        print(unstruct.extent)
        if True:
            trisurf = subsurface.TriSurf(unstruct)
            s = subsurface.visualization.to_pyvista_mesh(trisurf)
            subsurface.visualization.pv_plot([s], image_2d=True)

        return unstruct

    def test_put_file_in_project(self, liquid_earth_client, data_path):
        us = read_unstruct(data_path + '/interpolator_meshes.nc')
        print(us.extent)
        body, header = us.to_binary()

        liquid_earth_client._put_file_in_project(
            project_id="52f88baa-c84c-4082-bbba-869ef3819004",
            data_name="data_from_subsurface.le",
            data_type=DataTypes.static_mesh,
            file=body
        )

        liquid_earth_client._put_file_in_project(
            project_id="52f88baa-c84c-4082-bbba-869ef3819004",
            data_name="data_from_subsurface.json",
            data_type=DataTypes.static_mesh,
            file=header
        )
