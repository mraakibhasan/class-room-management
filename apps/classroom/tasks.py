# tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mass_mail
from django.conf import settings
from apps.classroom.models import Bookings, Rooms
from apps.authkit.models import User

def get_student_emails(batch):
    """Get all student emails from a specific batch"""
    if not batch:
        return []
    return list(User.objects.filter(
        batch=batch,
        role='Student'
    ).values_list('email', flat=True))

def format_notification_email(booking, notification_type):
    """Format email content based on notification type"""
    classroom = booking.classroom
    faculty = booking.faculty
    batch = booking.batch
    
    subjects = {
        'upcoming': f'Upcoming Class in {classroom.name} - Starting in 10 minutes',
        'started': f'Class Started in {classroom.name}',
        'completed': f'Class Completed in {classroom.name} - Feedback Required'
    }
    
    faculty_messages = {
        'upcoming': f"""Dear {faculty.username},
Your class in {classroom.name} will start in 10 minutes.

Details:
- Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
- Batch: {batch.name if batch else 'N/A'}
- Campus: {classroom.campus}

Please ensure you reach the classroom on time.""",
        
        'started': f"""Dear {faculty.username},
Your class in {classroom.name} has started.

Details:
- Duration: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
- Batch: {batch.name if batch else 'N/A'}
- Campus: {classroom.campus}""",
        
        'completed': f"""Dear {faculty.username},
Your class in {classroom.name} has been completed.

Thank you for using our classroom booking system."""
    }
    
    student_messages = {
        'upcoming': f"""Dear Student,
Your class in {classroom.name} will start in 10 minutes.

Details:
- Faculty: {faculty.username}
- Time: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
- Campus: {classroom.campus}

Please reach the classroom on time.""",
        
        'started': f"""Dear Student,
Your class in {classroom.name} has started.

Details:
- Faculty: {faculty.username}
- Duration: {booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}
- Campus: {classroom.campus}""",
        
        'completed': f"""Dear Student,
Your class in {classroom.name} has been completed.

Please take a moment to provide feedback about the classroom:
[Feedback Link Here]

Your feedback helps us maintain and improve our facilities.
Thank you!"""
    }
    
    return {
        'subject': subjects[notification_type],
        'faculty_message': faculty_messages[notification_type],
        'student_message': student_messages[notification_type]
    }

@shared_task
def schedule_class_notifications(booking_id):
    """Schedule all notifications for a booking"""
    try:
        booking = Bookings.objects.get(id=booking_id)
        
        # Schedule 10-minute warning
        notification_time = booking.start_time - timedelta(minutes=10)
        send_class_notification.apply_async(
            args=[booking_id, 'upcoming'],
            eta=notification_time
        )
        
        # Schedule start notification
        send_class_notification.apply_async(
            args=[booking_id, 'started'],
            eta=booking.start_time
        )
        
        # Schedule completion notification
        send_class_notification.apply_async(
            args=[booking_id, 'completed'],
            eta=booking.end_time
        )
        
    except Bookings.DoesNotExist:
        print(f"Booking {booking_id} not found")

@shared_task
def send_class_notification(booking_id, notification_type):
    """Send email notifications to faculty and students"""
    try:
        booking = Bookings.objects.get(id=booking_id)
        
        # Skip if booking is not approved
        if booking.status != 'Approved':
            return
        
        # Get email content
        email_content = format_notification_email(booking, notification_type)
        
        # Prepare faculty email
        faculty_email = booking.faculty.email
        
        # Get student emails
        student_emails = get_student_emails(booking.batch)
        
        # Prepare email messages
        messages = []
        
        # Faculty email
        messages.append((
            email_content['subject'],
            email_content['faculty_message'],
            settings.DEFAULT_FROM_EMAIL,
            [faculty_email]
        ))
        
        # Student emails (Send in batches if needed)
        if student_emails:
            messages.append((
                email_content['subject'],
                email_content['student_message'],
                settings.DEFAULT_FROM_EMAIL,
                student_emails
            ))
        
        # Send all emails
        send_mass_mail(messages, fail_silently=False)
        
    except Bookings.DoesNotExist:
        print(f"Booking {booking_id} not found")
    except Exception as e:
        print(f"Error sending notification: {str(e)}")

# Periodic task to clean up old bookings
@shared_task
def cleanup_old_bookings():
    """Clean up old bookings and ensure notifications are sent"""
    now = timezone.now()
    old_bookings = Bookings.objects.filter(
        end_time__lt=now,
        status='Approved'
    )
    
    for booking in old_bookings:
        # Send completion notification if not already sent
        send_class_notification.delay(booking.id, 'completed')