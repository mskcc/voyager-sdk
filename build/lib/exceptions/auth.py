class NotAuthenticatedException(Exception):
    """
    No Service or JWT token set
    """
    code = 100


class JWTTokenExpiredException(Exception):
    """
    JWT Tokens Expired
    """
    code = 101


class InvalidCredentialsException(Exception):
    """
    Invalid credentials
    """
    code = 102


class FailedToLoginException(Exception):
    """
    Failed to login
    """
    code = 103
