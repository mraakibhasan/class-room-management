from django.urls import path
from apps.classroom.views import *

urlpatterns = [
    path("class-room-list", ClassroomListAPIView.as_view(), name="class-room-list"),
    path('create-booking', BookingCreateAPIView.as_view(), name='create_booking'),
    path('my-bookings', MyBookingsAPIView.as_view(), name='my_bookings'),
    path('my-class-list', FacultyClassListAPIView.as_view(), name='my_class_list'),
    path('global-class-list', GlobalClassroomListAPIView.as_view(), name='global_class_list'),
]