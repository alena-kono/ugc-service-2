class AuthException(BaseException):
    """Base class for exceptions in this module."""


class AuthSignInException(AuthException):
    """Exception raised for errors during signing in."""


class AuthRetrieveUserDataException(AuthException):
    """Exception raised for errors during retrieving user data."""
