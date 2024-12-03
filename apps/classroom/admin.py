from django.contrib import admin
from apps.classroom.models import *

for model in [Rooms, Bookings, Feedbacks]:
    admin.site.register(model)
