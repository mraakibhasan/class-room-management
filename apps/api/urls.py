from django.urls import path, include
from apps.authkit.views import *

urlpatterns = [
    path("api/v1/", include("apps.authkit.urls")),
    path("api/v1/", include("apps.classroom.urls"))
]