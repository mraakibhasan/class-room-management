from django.urls import path
from apps.authkit.views import *

urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('login', LoginView.as_view(), name='login'),
    path('refresh-token', RefreshTokenView.as_view(), name='refresh-token'),
    path('logout', LogoutView.as_view(), name='logout'),
    path('profile', UserView.as_view(), name='profile'),
    path('is-authenticated', IsAuthenticatedView.as_view(), name='is-authenticated'),
]