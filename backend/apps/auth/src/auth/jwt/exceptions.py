from src.auth.exceptions import AuthError


class InvalidJWTError(AuthError):
    ...


class RevokedJWTError(AuthError):
    ...
