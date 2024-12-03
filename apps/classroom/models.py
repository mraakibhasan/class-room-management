from django.db import models
from apps.base.base_model import BaseModel
from apps.authkit.models import User, Batch

class Rooms(BaseModel):
    name = models.CharField(max_length=255)
    campus = models.CharField(max_length=255)
    capacity = models.IntegerField()
    computer_count = models.IntegerField(default=0)
    projector_count = models.IntegerField(default=0)
    whiteboard_count = models.IntegerField(default=0)
    duster_count = models.IntegerField(default=0)
    marker_count = models.IntegerField(default=0)
    speaker_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.name} - {self.campus}"
    
class Bookings(BaseModel):
    classroom = models.ForeignKey(Rooms, on_delete=models.CASCADE)
    faculty = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Faculty'})
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_hoc_booking = models.BooleanField(default=False)
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.classroom.name} booked by {self.faculty.username}"
    
class Feedbacks(BaseModel):
    booking = models.ForeignKey(Bookings, on_delete=models.CASCADE)
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    cleanliness_feedback = models.CharField(max_length=255, blank=True, null=True)
    equipment_feedback = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"Feedback by {self.student.username} for {self.booking.classroom.name}"
