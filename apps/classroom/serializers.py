from rest_framework import serializers
from apps.classroom.models import Rooms, Bookings, Feedbacks

class RoomsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rooms
        fields = '__all__'
        
class BookingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bookings
        fields = '__all__'
        
class FeedbacksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedbacks
        fields = '__all__'