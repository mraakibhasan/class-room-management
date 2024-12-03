from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from apps.base.base_response import base_success_response, base_error_response
from apps.authkit.serializers import *
from apps.authkit.authentication import CookieJWTAuthentication

#====== Registration API ======#
class RegisterView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = UserSerializer

    def post(self, request):
        try:
            data = request.data.copy()
            
            batch_name = data.get('batch', None)
            if batch_name:
                batch, created = Batch.objects.get_or_create(name=batch_name)
                data['batch'] = batch.id
            
            serializer = UserSerializer(data=data)
            
            if serializer.is_valid():
                user = serializer.save()
            
                data = {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
                
                if data['role'] == 'Student':
                    data['batch'] = batch_name
                
                return Response(
                    base_success_response('Account registered successfully.', data),
                    status=status.HTTP_201_CREATED
                )

            return Response(
                base_error_response('Account registration failed.', serializer.errors),
                status=status.HTTP_400_BAD_REQUEST
            )

        except KeyError as e:
            return Response(
                base_error_response('Account registration failed.', str(e)),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                base_error_response('Account registration failed.', str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
#====== Login API ======#
class LoginView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer
    
    def post(self, request, *args, **kwargs):
        try:
            username = request.data.get('username')
            password = request.data.get('password')
            remember_me = request.data.get('remember_me', False)

            if not username or not password:
                return Response({"error": "Username and password are required"}, status=status.HTTP_400_BAD_REQUEST)

            user = authenticate(username=username, password=password)

            if user is not None:
                refresh_token = RefreshToken.for_user(user)
                access_token = str(refresh_token.access_token)
                        
                data = {
                    'access_token': access_token,
                    'refresh_token': str(refresh_token),
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
                
                if data['role'] == 'Student':
                    data['batch'] = user.batch.name
                    
                response = Response(
                    base_success_response('Logged in successfully.', data),
                    status=status.HTTP_200_OK
                )

                cookie_max_age = 60 * 60 * 24 * 30
                
                if remember_me:
                    response.set_cookie(
                        key='refresh_token',
                        value=str(refresh_token),
                        httponly=True,
                        secure=True, 
                        samesite='None',
                        max_age=cookie_max_age
                    )
                
                response.set_cookie(
                    key='access_token',
                    value=access_token,
                    httponly=True,
                    secure=True, 
                    samesite='None',
                    max_age=cookie_max_age
                )

                return response
            else:
                return Response(
                    base_error_response('Invalid username or password.'),
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        except KeyError as e:
            return Response(
                base_error_response('Login failed.', f'Missing key: {str(e)}'),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                base_error_response('Login failed.', str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#====== Refresh Token API ======#
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        refresh_token_str = None
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            refresh_token_str = auth_header.split(' ')[1]

        if not refresh_token_str:
            refresh_token_str = request.COOKIES.get('refresh_token')

        if refresh_token_str:
            try:
                old_refresh_token = RefreshToken(refresh_token_str)
                old_refresh_token.blacklist()

                payload = old_refresh_token.payload
                user_id = payload.get('user_id')
                user = User.objects.get(id=user_id)

                new_refresh_token = RefreshToken.for_user(user)
                new_access_token = str(new_refresh_token.access_token)

                data = {
                    'access_token': new_access_token,
                    'refresh_token': str(new_refresh_token),
                }
                
                response = Response(
                    base_success_response('Token refreshed successfully.', data),
                    status=status.HTTP_200_OK
                )
                
                cookie_max_age = 60 * 60 * 24 * 30
                
                response.set_cookie(
                    key='refresh_token',
                    value=str(new_refresh_token),
                    httponly=True,
                    secure=True, 
                    samesite='None',
                    max_age=cookie_max_age
                )
                
                response.set_cookie(
                    key='access_token',
                    value=new_access_token,
                    httponly=True,
                    secure=True, 
                    samesite='None',
                    max_age=cookie_max_age
                )
                return response

            except User.DoesNotExist:
                return Response(
                    base_error_response('User not found.'),
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                return Response(
                    base_error_response('Token refresh failed.', str(e)),
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        else:
            return Response(
                base_error_response('Refresh token is required. Not found in cookies or header.'),
                status=status.HTTP_400_BAD_REQUEST
            )

#==== Logout API ====#
class LogoutView(APIView):
    
    def post(self, request):
        refresh_token = request.COOKIES.get('refresh_token', None)
        
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception as e:
                pass

        response = Response(
            base_success_response('You have been logged out.'),
            status=status.HTTP_200_OK
        )

        cookie_max_age = 60 * 60 * 24 * 30
        
        response.set_cookie(
            key='refresh_token',
            value='',
            httponly=True,
            secure=True, 
            samesite='None',
            max_age=cookie_max_age
        )
        response.set_cookie(
            key='access_token',
            value='',
            httponly=True,
            secure=True, 
            samesite='None',
            max_age=cookie_max_age
        )

        return response

#====== User Get API ======#
class UserView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            user = request.user
            data = {
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
            
            if data['role'] == 'Student':
                data['batch'] = user.batch.name
                
            return Response(
                base_success_response('User details fetched successfully.', data),
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                base_error_response('User details fetch failed.', str(e)),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
#===== Is Authenticated API =====#
class IsAuthenticatedView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if request.user.is_authenticated:
            data = {
                'is_authenticated': True,
                'user_id': request.user.id,
                'username': request.user.username,
                'email': request.user.email,
                'role': request.user.role
            }
            
            if data['role'] == 'Student':
                data['batch'] = request.user.batch.name
                
            return Response(
                base_success_response('Authenticated successfully.', data),
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                base_error_response('Not authenticated.'),
                status=status.HTTP_401_UNAUTHORIZED
            )