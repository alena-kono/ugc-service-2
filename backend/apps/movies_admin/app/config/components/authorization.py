from enum import StrEnum, auto

import environ

env = environ.Env()

AUTH_API_LOGIN_URL = env("AUTH_API_URL")
AUTH_JWT_ENCODING_ALGORITHM = env("AUTH_JWT_ENCODING_ALGORITHM")
AUTH_JWT_SECRET_KEY = env("AUTH_JWT_SECRET_KEY")

REQUEST_TIMEOUT = 5

AUTHENTICATION_BACKENDS = [
    "user.authorization.CustomBackend",
]


class Permissions(StrEnum):
    user_can_create_content = auto()
