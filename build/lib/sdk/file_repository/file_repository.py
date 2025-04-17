from config import Config
from api import VoyagerAPI
from .file import File
from urllib.parse import urljoin
from voyager_sdk.paggination import VoyagerAPIIterator

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
        elif path_regex:
            params["path_regex"] = path_regex
        elif file_type:
            params["file_type"] = file_type
        elif file_name:
            params["file_name"] = file_name
        elif file_name_regex:
            params["file_name_regex"] = file_name
        elif file_group:
            params["file_group"] = file_group
        elif metadata:
            params["metadata"] = metadata
        elif metadata_regex:
            params["metadata_regex"] = metadata_regex
        elif values_metadata:
            # TODO: This doesn't return File objects
            params["values_metadata"] = values_metadata
        return VoyagerAPIIterator(endpoint, params, File)
