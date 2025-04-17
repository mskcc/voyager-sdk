import requests
from config import Config
from urllib.parse import urljoin
from api.voyager import VoyagerAPI
from exceptions.auth_exceptions import AuthenticationException, JWTTokenExpiredException, FailedToLoginException, \
    InvalidCredentialsException

config = Config()
api = VoyagerAPI()


class Authenticator(object):

    @staticmethod
    def login(username, password):
        response = requests.post(urljoin(config.base_url, VoyagerAPI.LOGIN), {
            "username": username, "password": password})
        if response.status_code == 200:
            config.auth_token = response.json()["access"]
            config.refresh_token = response.json()["refresh"]
            config.email = response.json()["user"]["email"]
            return response.json()
        elif response.status_code == 401:
            raise InvalidCredentialsException(f"Invalid credentials for user {username}")
        else:
            raise FailedToLoginException()

    @staticmethod
    def verify():
        """
        Verify JWT token  and if expired try to refresh it. Return true if succssesful or false if fail
        :return: bool
        """
        response = requests.post(config.base_url, {"token": config.auth_token})
        if response.status_code == 200:
            return True
        else:
            response = requests.post(urljoin(config.base_url, VoyagerAPI.REFRESH), {
                "refresh": config.refresh_token})
            if response.status_code == 200:
                config.auth_token = response.json()["access"]
                config.refresh_token = response.json()["refresh"]
                return True
        return False

    @staticmethod
    def get_auth():
        if config.mode == "SERVICE":
            return {
                "type": "SERVICE",
                "token": config.service_token
            }
        elif config.mode == "LOCAL":
            if not Authenticator.verify():
                raise JWTTokenExpiredException()
            return {
                "type": "JWT",
                "access": config.auth_token,
                "refresh": config.refresh_token
            }
        else:
            raise AuthenticationException()
