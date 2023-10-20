import http
import logging

import requests
from config.components import authorization
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from jose import jwt
from user.exceptions import (
    AuthException,
    AuthRetrieveUserDataException,
    AuthSignInException,
)
from user.models import User

logger = logging.getLogger(__name__)


def signin(username: str, password: str) -> tuple[str, str]:
    """
    Sign in to the Auth service.

    curl -X 'POST' \
    'http://127.0.0.1:8001/api/v1/auth/signin' \
    -H 'accept: application/json' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    -d 'username=<>&password=<>'

    return: user_id, access_token
    """
    url = f"{authorization.AUTH_API_LOGIN_URL}/api/v1/auth/signin"
    payload = f"username={username}&password={password}"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    try:
        response = requests.post(
            url,
            data=payload,
            headers=headers,
            timeout=authorization.REQUEST_TIMEOUT,
        )
    except requests.exceptions.RequestException:
        raise AuthSignInException("The Auth service is unavailable.")

    if response.status_code != http.HTTPStatus.OK:
        raise AuthSignInException("Received an error during signing in.")

    data = response.json()

    access_token = data["access_token"]

    jwt_claims = jwt.decode(
        access_token,
        authorization.AUTH_JWT_SECRET_KEY,
        algorithms=[authorization.AUTH_JWT_ENCODING_ALGORITHM],
    )

    user_id = jwt_claims["user"]["id"]

    return user_id, access_token


def retrieve_user_data(user_id: str, access_token: str) -> dict[str, str]:
    url = f"{authorization.AUTH_API_LOGIN_URL}/api/v1/users/{user_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    user_response = requests.get(
        url,
        headers=headers,
        timeout=authorization.REQUEST_TIMEOUT,
    )

    if user_response.status_code != http.HTTPStatus.OK:
        raise AuthRetrieveUserDataException("The Users detail cannot be retrieved.")

    return user_response.json()


def create_user(
    user_id: str, first_name: str, last_name: str, username: str, password: str
) -> User:
    user_model = get_user_model()

    user = user_model.objects.create_user(
        id=user_id,
        username=username,
        password=password,
        first_name=first_name,
        last_name=last_name,
    )

    return user


def get_user_by_username(username: str) -> User | None:
    """
    Get user by username.

    The function is used in use case when the Auth service is unavailable.


    params:
        username: str

    return: User | None
    """
    user_model = get_user_model()

    try:
        return user_model.objects.get(username=username)
    except user_model.DoesNotExist:
        return None


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user_id, access_token = signin(username, password)

            if user := self.get_user(user_id):
                return user

            user_data = retrieve_user_data(user_id, access_token)
        except (KeyError, AuthException):
            logger.warning(
                "The Auth service is unavailable. "
                "The local storage will be used for the auth."
            )

            user = get_user_by_username(username)

            if user and user.check_password(password):
                return user

            return None

        user = create_user(
            user_id=user_data["id"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            username=username,
            password=password,
        )

        return user

    def get_user(self, user_id):
        user_model = get_user_model()
        try:
            return user_model.objects.get(pk=user_id)
        except user_model.DoesNotExist:
            return None
