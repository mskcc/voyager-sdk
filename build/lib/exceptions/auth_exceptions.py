class AuthenticationException(Exception):
    """
    No Service or JWT token set
    """
    code = 200


class JWTTokenExpiredException(Exception):
    """
    JWT Tokens Expired
    """
    code = 201


class InvalidCredentialsException(Exception):
    """
    Invalid credentials
    """
    code = 202


class FailedToLoginException(Exception):
    """
    Failed to login
    """
    code = 203
