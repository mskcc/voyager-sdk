import requests
from config import Config
from api import VoyagerAPI
from urllib.parse import urljoin
from .file import File
from auth import Authenticator
from voyager_sdk.paggination import VoyagerAPIIterator
from exceptions.base_exceptions import ConfigurationException
from exceptions.auth_exceptions import JWTTokenExpiredException, AuthenticationException

config = Config()


class FileRepository(object):

    @classmethod
    def filter(
            cls,
            path=None,
            path_regex=None,
            file_type=None,
            file_name=None,
            file_name_regex=None,
            file_group=None,
            metadata=[],
            metadata_regex=[],
            values_metadata=None
    ):
        endpoint = urljoin(config.base_url, VoyagerAPI.FILES)
        params = dict()
        if path:
            params["path"] = path
        if path_regex:
            params["path_regex"] = path_regex
        if file_type:
            params["file_type"] = file_type
        if file_name:
            params["filename"] = file_name
        if file_name_regex:
            params["filename_regex"] = file_name
        if file_group:
            params["file_group"] = file_group
        if metadata:
            params["metadata"] = metadata
        if metadata_regex:
            params["metadata_regex"] = metadata_regex
        if values_metadata:
            # TODO: This doesn't return File objects
            params["values_metadata"] = values_metadata
        return VoyagerAPIIterator(endpoint, params, File)

    def get_by_id(self, bid):
        endpoint = urljoin(config.base_url, f"{VoyagerAPI.FILES}/{bid}/")
        try:
            auth = Authenticator.get_auth()
        except JWTTokenExpiredException as e:
            raise AuthenticationException(f"Failed to authenticate for {self.base_url}")
        except AuthenticationException as e:
            raise AuthenticationException(f"Failed to authenticate for {self.base_url}")
        if auth["type"] == "JWT":
            authorization = {"Authorization": f"Bearer {self.config.auth_token}"}
        elif auth["type"] == "SERVICE":
            authorization = {"Authorization": f"Token {self.config.service_token}"}
        else:
            raise ConfigurationException(f"Unknown mode: {self.config.mode}")
        response = requests.get(endpoint, headers=authorization)
        response.raise_for_status()
        return File.from_json(response.json())
