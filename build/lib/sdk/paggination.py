import requests
from config import Config
from auth import Authenticator
from exceptions.base_exceptions import ConfigurationException
from exceptions.auth_exceptions import JWTTokenExpiredException, AuthenticationException


class PaginatedAPIIterator(object):

    config = Config()

    def __init__(self, base_url, params=None, result_class=None, page_param="page", per_page_param="page_size", per_page=10):
        """
        Initialize the iterator.

        :param base_url: The base URL of the API endpoint.
        :param params: Additional query parameters for the API request.
        :param page_param: The query parameter name for the page number.
        :param per_page_param: The query parameter name for the number of items per page.
        :param per_page: The number of items to fetch per page.
        """
        self.base_url = base_url
        self.params = params or {}
        self.result_class = result_class
        self.page_param = page_param
        self.per_page_param = per_page_param
        self.per_page = per_page
        self.current_page = 1
        self.current_items = []
        self.has_more = True

    def __iter__(self):
        """Make the class iterable."""
        return self

    def __next__(self):
        """Fetch the next item from the API."""
        if not self.current_items and not self.has_more:
            raise StopIteration

        if not self.current_items:
            self._fetch_next_page()

        return self.current_items.pop(0)

    def _fetch_next_page(self):
        """Fetch the next page of items from the API."""
        params = {**self.params, self.page_param: self.current_page, self.per_page_param: self.per_page}
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
        response = requests.get(self.base_url,
                                headers=authorization,
                                params=params)
        response.raise_for_status()
        data = response.json()
        if self.result_class:
            self.current_items = [self.result_class.from_json(f) for f in data.get("results", [])]
        else:
            self.current_items = data.get("results", [])
        self.has_more = data.get("page") is not None
        self.current_page += 1
