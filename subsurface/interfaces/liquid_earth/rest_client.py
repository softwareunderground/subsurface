import json
import uuid
from enum import Enum, auto

import requests


class DataTypes(Enum):
    static_mesh = "static_mesh"
    collars = "wells/collars"
    cylinder = "wells/cylinders"
    volumes = "volumes"


class LiquidEarthClient():
    token: str
    user_id: str

    # Move to local settings
    host = "https://apim-liquidearth.azure-api.net/"

    @property
    def header(self):
        header_dict = {
            "Authorization": f"Bearer {self.token}"
        }
        return header_dict

    def login(self, username: str, password: str):
        end_point = "user/login_b2c"

        data = {
            "username": username,
            "password": password,
            "grant_type": "password",
            "client_id": "685e08c0-0aac-42f6-80a9-c57440cd2962",
            "scope": "openid 685e08c0-0aac-42f6-80a9-c57440cd2962 offline_access"
        }

        response = requests.post(self.host + end_point, data=data)
        if response.status_code == 400:
            raise Exception(f"Request failed: {response.text}")
        elif response.status_code == 200:
            _json = response.json()
            self.token = _json["access_token"]
            self.user_id = username

    def get_available_projects(self):
        end_point = "cosmos-le/v1/available_projects/"
        response = requests.get(self.host + end_point, headers=self.header)

        if response.status_code >= 400:
            raise Exception(f"Request failed: {response.text}")
        elif response.status_code >= 200:
            print(response.json())
            return response.json()

    def add_new_project(self, project_name, extent, project_id=None):
        if project_id is None:
            project_id = str(uuid.uuid4())

        available_projects: list = self.get_available_projects()

        for project in available_projects:
            if project["project_id"] == project_id:
                raise ValueError("This Project already exists")

        new_project = {
            "project_name": project_name,
            "project_id": project_id
        }
        available_projects.append(new_project)
        self._post_available_projects(available_projects)

        new_project_meta = {
            "remote_name": project_name,
            "id": project_id,
            "owner": self.user_id,
            "extent": extent,
            "static_data_address": []
        }
        self._post_project_meta(new_project_meta)
        return project_id

    def add_data_to_project(self, project_id: str, data_name: str, data_type: DataTypes,
                            header: json, body: bytearray):

        self._post_update_meta_data(project_id, data_name, data_type)
        self._put_file_in_project(project_id, data_name + ".le", data_type, body)
        self._put_file_in_project(project_id, data_name + ".json", data_type,  json.dumps(header))

    def _put_file_in_project(self, project_id: str, data_name, data_type: DataTypes, file):
        blob_path = data_type.value + "/" + data_name

        end_point = f"container/{project_id}/{blob_path}"
        response = requests.put(self.host + end_point, data=file, headers=self.header)

        if response.status_code >= 400:
            raise Exception(f"Request failed: {response.text}")
        elif response.status_code >= 200:
            print(response.text)

    def _post_update_meta_data(self, project_id: str, data_name: str, data_type: DataTypes):

        query_param = f"?project_id={project_id}&data_id={data_name}&data_type={data_type.value}"
        end_point = "subsurface-lite/v1/update_project_meta" + query_param

        response = requests.post(end_point)

        if response.status_code >= 400:
            raise Exception(f"Request failed: {response.text}")
        elif response.status_code >= 200:
            print(response.text)

    def _post_available_projects(self, available_projects: list):
        end_point = "cosmos-le/v1/available_projects/"
        response = requests.post(self.host + end_point, json=available_projects,
                                 headers=self.header)

        if response.status_code >= 400:
            raise Exception(f"Request failed: {response.text}")
        elif response.status_code >= 200:
            print("Available Projects Posted")

    def _post_project_meta(self, meta_data: dict):
        project_id = meta_data["id"]

        end_point = f"cosmos-le/v1/project_meta/?project_id={project_id}"
        response = requests.post(self.host + end_point, json=meta_data, headers=self.header)

        if response.status_code >= 400:
            raise Exception(f"Request failed: {response.text}")
        elif response.status_code >= 200:
            print("Project Metadata Posted")
