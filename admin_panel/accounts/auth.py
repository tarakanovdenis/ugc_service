import http
from enum import Enum  # StrEnum, auto


import jwt
import requests
from django.http import HttpRequest
from django.conf import settings
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model


User = get_user_model()


class DefaultRoleEnum(Enum):
    ADMIN = 'admin'
    SIMPLE_USER = 'simple_user'
    SUPER_USER = 'super_user'


class CustomBackend(BaseBackend):
    def authenticate(self, request: HttpRequest, username=None, password=None):
        # Check the username/password and return a user

        request_id = request.headers.get('X-Request-Id')

        url = settings.AUTH_API_LOGIN_URL
        payload = {'username': username, 'password': password}
        response = requests.post(
            url,
            data=payload,
            headers={'X-Request-Id': request_id}
        )

        if response.status_code != http.HTTPStatus.OK:
            return None

        data = response.json()

        decoded_jwt = jwt.decode(
            data['access_token'],
            key=settings.PUBLIC_KEY_PATH.read_text(),
            algorithms=[settings.ALGORITHM]
        )

        try:
            user, created = User.objects.get_or_create(
                id=decoded_jwt.get('user_id')
            )
            user.username = decoded_jwt.get('sub')
            user.email = decoded_jwt.get('email')
            user.first_name = decoded_jwt.get('first_name')
            user.last_name = decoded_jwt.get('last_name')

            user_role_str: str = decoded_jwt.get('role')
            user_role_list = user_role_str.split(' ')

            if DefaultRoleEnum.SUPER_USER.value in user_role_list:
                user.is_superuser = True

            if DefaultRoleEnum.SUPER_USER.value in user_role_list or DefaultRoleEnum.ADMIN.value in user_role_list:
                user.is_staff = True

            user.save()

        except Exception:
            return None

        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
