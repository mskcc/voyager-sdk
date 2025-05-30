import json

import requests
from config import Config
from api import VoyagerAPI
from auth import Authenticator
from urllib.parse import urljoin
from exceptions.auth_exceptions import JWTTokenExpiredException, AuthenticationException

config = Config()


class VoyagerClient(object):

    @staticmethod
    def register_pipeline(pipeline_type, name, github, version, entrypoint, output_directory, output_file_group):
        endpoint = urljoin(config.base_url, f"{VoyagerAPI.PIPELINES}/")
        try:
            auth = Authenticator.get_auth()
        except JWTTokenExpiredException as e:
            raise AuthenticationException(f"Failed to authenticate for {config.base_url}")
        except AuthenticationException as e:
            raise AuthenticationException(f"Failed to authenticate for {config.base_url}")
        if auth["type"] == "JWT":
            authorization = {"Authorization": f"Bearer {config.auth_token}"}
        else:
            raise AuthenticationException(f"Need to login to run command")
        body = {
            "pipeline_type": pipeline_type,
            "name": name,
            "github": github,
            "version": version,
            "entrypoint": entrypoint,
            "output_directory": output_directory,
            "output_file_group": output_file_group
        }
        response = requests.post(endpoint, data=body, headers=authorization)
        print(response.json())
        response.raise_for_status()
        return response.json()

    @staticmethod
    def run_pipeline(name, pipeline, inputs, tags, output_directory):
        endpoint = urljoin(config.base_url, f"{VoyagerAPI.RUN}/")
        try:
            auth = Authenticator.get_auth()
        except JWTTokenExpiredException as e:
            raise AuthenticationException(f"Failed to authenticate for {config.base_url}")
        except AuthenticationException as e:
            raise AuthenticationException(f"Failed to authenticate for {config.base_url}")
        if auth["type"] == "JWT":
            authorization = {"Authorization": f"Bearer {config.auth_token}"}
        else:
            raise AuthenticationException(f"Need to login to run command")
        body = {
            "name": name,
            "app": pipeline,
            "inputs": inputs,
            "tags": tags,
            "output_directory": output_directory
        }
        response = requests.post(endpoint, json=body, headers=authorization)
        print(response.json())
        response.raise_for_status()
        return response.json()
