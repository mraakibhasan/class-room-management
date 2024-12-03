from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.authkit.models import User
from django.conf import settings
import jwt
from rest_framework.exceptions import APIException


class CustomAuthenticationFailed(APIException):
    status_code = 401
    default_detail = 'Authentication failed.'
    default_code = 'authentication_failed'

    def __init__(self, detail=None, code=None, status_code=None):
        if status_code is not None:
            self.status_code = status_code
        super().__init__(detail, code)


class CookieJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        token = None

        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

        if not token:
            token = request.COOKIES.get('access_token')

        if not token:
            raise CustomAuthenticationFailed({
                'status': 'error',
                'message': 'Authentication credentials were not provided.',
            }, status_code=401)

        try:
            payload = jwt.decode(
                token,
                settings.SIMPLE_JWT['SIGNING_KEY'],
                algorithms=[settings.SIMPLE_JWT['ALGORITHM']]
            )
        except jwt.ExpiredSignatureError:
            raise CustomAuthenticationFailed({
                'status': 'error',
                'message': 'Token is expired.',
            }, status_code=401)
        except jwt.InvalidTokenError:
            raise CustomAuthenticationFailed({
                'status': 'error',
                'message': 'Invalid token.',
            }, status_code=401)

        try:
            user = User.objects.get(id=payload['user_id'])
        except User.DoesNotExist:
            raise CustomAuthenticationFailed({
                'status': 'error',
                'message': 'User not found.',
            }, status_code=401)

        return (user, token)