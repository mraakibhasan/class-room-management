from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import datetime
from rest_framework.permissions import IsAuthenticated
from apps.authkit.authentication import CookieJWTAuthentication
from apps.base.base_response import base_success_response, base_error_response
from apps.classroom.serializers import *
from apps.classroom.models import *
from apps.classroom.tasks import schedule_class_notifications

class ClassroomListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        
        # Handle query parameters with proper error handling
        try:
            # Only add filters if the parameter exists and is not empty
            filter_conditions = {}
            
            if request.query_params.get('capacity'):
                filter_conditions['capacity__gte'] = int(request.query_params['capacity'])
            
            if request.query_params.get('computer_count'):
                filter_conditions['computer_count__gte'] = int(request.query_params['computer_count'])
                
            if request.query_params.get('projector_count'):
                filter_conditions['projector_count__gte'] = int(request.query_params['projector_count'])
                
            if request.query_params.get('whiteboard_count'):
                filter_conditions['whiteboard_count__gte'] = int(request.query_params['whiteboard_count'])
                
            if request.query_params.get('duster_count'):
                filter_conditions['duster_count__gte'] = int(request.query_params['duster_count'])
                
            if request.query_params.get('marker_count'):
                filter_conditions['marker_count__gte'] = int(request.query_params['marker_count'])
                
            if request.query_params.get('speaker_count'):
                filter_conditions['speaker_count__gte'] = int(request.query_params['speaker_count'])

            # Handle campus filter
            campus = request.query_params.get('campus')
            if campus:
                filter_conditions['campus'] = campus

            # Store applied filters for response
            applied_filters = {
                key.replace('__gte', ''): value 
                for key, value in filter_conditions.items()
                if key != 'campus'
            }
            if campus:
                applied_filters['campus'] = campus

        except ValueError:
            return Response(
                base_error_response("Invalid filter parameters. Please ensure all counts are valid numbers."),
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get filtered classrooms
        classrooms = Rooms.objects.all()
        if filter_conditions:
            classrooms = classrooms.filter(**filter_conditions)

        classroom_data = []

        for classroom in classrooms:
            # Rest of the code remains the same as before
            current_booking = Bookings.objects.filter(
                classroom=classroom,
                start_time__lte=now,
                end_time__gt=now,
                status='Approved'
            ).first()

            future_bookings = Bookings.objects.filter(
                classroom=classroom,
                start_time__gt=now,
                status='Approved'
            ).order_by('start_time')

            next_booking = future_bookings.first()

            if current_booking:
                time_until_free = round((current_booking.end_time - now).total_seconds() / 3600, 2)
                total_duration = round((current_booking.end_time - current_booking.start_time).total_seconds() / 3600, 2)
                time_elapsed = round((now - current_booking.start_time).total_seconds() / 3600, 2)
                
                status_text = (f"Occupied ({time_until_free:.2f} hours remaining out of {total_duration:.2f} hours, "
                             f"{time_elapsed:.2f} hours elapsed)")
                
                current_booking_info = {
                    'faculty': current_booking.faculty.username,
                    'start_time': current_booking.start_time,
                    'end_time': current_booking.end_time,
                    'batch': current_booking.batch.name if current_booking.batch else None,
                    'total_duration_hours': total_duration,
                    'remaining_hours': time_until_free,
                    'elapsed_hours': time_elapsed,
                    'formatted_time': f"{current_booking.start_time.strftime('%I:%M %p')} - {current_booking.end_time.strftime('%I:%M %p')}"
                }
            else:
                if next_booking:
                    time_until_next = round((next_booking.start_time - now).total_seconds() / 3600, 2)
                    if time_until_next <= 24:
                        status_text = f"Available (Next class in {time_until_next:.1f} hours)"
                    else:
                        days_until_next = round(time_until_next / 24, 1)
                        status_text = f"Available (Next class on {next_booking.start_time.strftime('%B %d at %I:%M %p')})"
                else:
                    status_text = "Available (No upcoming bookings)"
                time_until_free = None
                current_booking_info = None

            next_bookings_info = []
            for booking in future_bookings[:3]:
                time_until_start = round((booking.start_time - now).total_seconds() / 3600, 2)
                duration = round((booking.end_time - booking.start_time).total_seconds() / 3600, 2)
                next_bookings_info.append({
                    'start_time': booking.start_time,
                    'end_time': booking.end_time,
                    'faculty': booking.faculty.username,
                    'batch': booking.batch.name if booking.batch else None,
                    'duration_hours': duration,
                    'hours_until_start': time_until_start,
                    'formatted_time': f"{booking.start_time.strftime('%B %d, %I:%M %p')} - {booking.end_time.strftime('%I:%M %p')} ({duration} hours)"
                })

            classroom_data.append({
                'classroom': RoomsSerializer(classroom).data,
                'status': status_text,
                'hours_until_free': time_until_free,
                'current_booking': current_booking_info,
                'upcoming_bookings': next_bookings_info,
                'applied_filters': applied_filters
            })
        
        if len(classroom_data) == 0:
            return Response(
                base_error_response("No classrooms found matching the specified criteria"),
                status=status.HTTP_200_OK
            )
            
        return Response(
            base_success_response(
                f"Found {len(classroom_data)} classroom(s) matching the criteria",
                {
                    'classrooms': classroom_data
                }
            ),
            status=status.HTTP_200_OK
        )
        
class BookingCreateAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        classroom_id = request.data.get('classroom_id')
        start_time = request.data.get('start_time')
        end_time = request.data.get('end_time')
        batch = request.data.get('batch', None)
        is_hoc_booking = request.data.get('is_hoc_booking', False)

        try:
            start_time = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
            end_time = datetime.strptime(end_time, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            return Response(
                base_error_response("Invalid date format. Please use YYYY-MM-DDTHH:MM:SS"),
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            classroom = Rooms.objects.get(id=classroom_id)
        except Rooms.DoesNotExist:
            return Response(
                base_error_response("Classroom not found."),
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.role != 'Faculty':
            return Response(
                base_error_response("Only Faculty can book classrooms."),
                status=status.HTTP_403_FORBIDDEN
            )

        overlapping_booking = Bookings.objects.filter(
            classroom=classroom,
            start_time__lt=end_time,
            end_time__gt=start_time
        ).exists()

        booking_status = 'Pending' if is_hoc_booking else 'Approved'
        
        if not is_hoc_booking and overlapping_booking:
            return Response(
                base_error_response("Classroom is already booked during this time."),
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            batch_obj = Batch.objects.get(name=batch)
        except Batch.DoesNotExist:
            return Response(
                base_error_response("Batch not found."),
                status=status.HTTP_400_BAD_REQUEST
            )

        booking = Bookings.objects.create(
            classroom=classroom,
            faculty=user,
            batch=batch_obj,
            start_time=start_time,
            end_time=end_time,
            is_hoc_booking=is_hoc_booking,
            status=booking_status
        )

        # Schedule notifications if booking is approved
        if booking_status == 'Approved':
            schedule_class_notifications.delay(booking.id)

        return Response(
            base_success_response("Booking created successfully.", BookingsSerializer(booking).data),
            status=status.HTTP_201_CREATED
        )
        
class MyBookingsAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'Faculty':
            return Response(
                base_error_response("Only Faculty can access booking history"),
                status=status.HTTP_403_FORBIDDEN
            )

        now = timezone.now()
        
        # Get query parameters for filtering
        booking_status = request.query_params.get('status')
        date_range = request.query_params.get('date_range')  # past/upcoming/all
        
        # Start with all bookings for this faculty
        bookings = Bookings.objects.filter(faculty=request.user)
        
        # Apply status filter if provided
        if booking_status and booking_status in dict(Bookings.STATUS_CHOICES):
            bookings = bookings.filter(status=booking_status)
        
        # Apply date range filter
        if date_range:
            if date_range == 'upcoming':
                bookings = bookings.filter(start_time__gt=now)
            elif date_range == 'past':
                bookings = bookings.filter(end_time__lt=now)
        
        # Order by start time
        bookings = bookings.order_by('start_time')
        
        bookings_data = []
        for booking in bookings:
            # Calculate if the booking is currently active
            is_active = (
                booking.start_time <= now and 
                booking.end_time > now and 
                booking.status == 'Approved'
            )
            
            # Format datetime to readable string
            formatted_date = booking.start_time.strftime('%B %d, %Y')
            formatted_time = f"{booking.start_time.strftime('%I:%M %p')} - {booking.end_time.strftime('%I:%M %p')}"
            
            bookings_data.append({
                'id': booking.id,
                'name': booking.classroom.name,
                'campus': booking.classroom.campus,
                'capacity': booking.classroom.capacity,
                'available': not is_active,
                'booking_status': booking.status,
                'date': formatted_date,
                'time': formatted_time,
                'batch': booking.batch.name if booking.batch else None,
                'resources': {
                    'computers': booking.classroom.computer_count,
                    'projectors': booking.classroom.projector_count,
                    'whiteboards': booking.classroom.whiteboard_count,
                    'speakers': booking.classroom.speaker_count
                }
            })

        if not bookings_data:
            return Response(
                base_error_response("No bookings found"),
                status=status.HTTP_200_OK
            )
            
        return Response(
            base_success_response(
                "Bookings retrieved successfully",
                bookings_data  # Direct list of bookings
            ),
            status=status.HTTP_200_OK
        )
        
        
class FacultyClassListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.role != 'Faculty':
            return Response(
                base_error_response("Only faculty can access their class list"),
                status=status.HTTP_403_FORBIDDEN
            )

        now = timezone.now()
        
        # Get query parameters for filtering
        date_filter = request.query_params.get('date')
        try:
            if date_filter:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
            else:
                filter_date = now.date()
        except ValueError:
            return Response(
                base_error_response("Invalid date format. Use YYYY-MM-DD"),
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get faculty's bookings for the specified date
        # Changed to include all statuses, not just Approved
        bookings = Bookings.objects.filter(
            faculty=request.user,
            start_time__date=filter_date
        ).order_by('start_time')

        classes = []
        for booking in bookings:
            # Determine class status based on time and booking status
            if booking.status == 'Pending':
                class_status = 'Pending Approval'
            elif booking.status == 'Rejected':
                class_status = 'Rejected'
            else:  # Approved
                if now < booking.start_time:
                    class_status = 'Upcoming'
                elif booking.start_time <= now <= booking.end_time:
                    class_status = 'Ongoing'
                else:
                    class_status = 'Completed'

            classes.append({
                'batch': booking.batch.name if booking.batch else None,
                'room': booking.classroom.name,
                'from': booking.start_time.strftime('%I:%M %p'),
                'to': booking.end_time.strftime('%I:%M %p'),
                'hocBooking': booking.is_hoc_booking,
                'date': booking.start_time.strftime('%Y-%m-%d'),
                'formatted_date': booking.start_time.strftime('%B %d, %Y'),
                'booking_status': booking.status,
                'class_status': class_status
            })

        if not classes:
            return Response(
                base_error_response(f"No classes found for {filter_date.strftime('%B %d, %Y')}"),
                status=status.HTTP_200_OK
            )
            
        return Response(
            base_success_response(
                f"Classes for {filter_date.strftime('%B %d, %Y')}",
                classes
            ),
            status=status.HTTP_200_OK
        )
        
class GlobalClassroomListAPIView(APIView):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        classrooms = Rooms.objects.all()
        
        classroom_list = []
        
        for classroom in classrooms:
            # Get current booking
            current_booking = Bookings.objects.filter(
                classroom=classroom,
                start_time__lte=now,
                end_time__gt=now,
                status='Approved'
            ).first()

            # Get next booking if room is currently occupied
            if current_booking:
                free_time = current_booking.end_time
            else:
                next_booking = Bookings.objects.filter(
                    classroom=classroom,
                    start_time__gt=now,
                    status='Approved'
                ).order_by('start_time').first()
                
                # If there's no next booking, use current time as free time
                free_time = next_booking.start_time if next_booking else now

            # Create the classroom object with the specified structure
            classroom_obj = {
                "id": classroom.id,
                "name": classroom.name,
                "capacity": classroom.capacity,
                "available": not current_booking,
                "freeTime": free_time.isoformat(),
                "equipment": {
                    "computers": classroom.computer_count,
                    "projectors": classroom.projector_count,
                    "whiteboards": classroom.whiteboard_count,
                    "dusters": classroom.duster_count,
                    "speakers": classroom.speaker_count,
                    "markers": classroom.marker_count
                }
            }

            # Add additional useful information
            classroom_obj.update({
                "campus": classroom.campus,
                "current_status": {
                    "occupied": bool(current_booking),
                    "current_booking": {
                        "faculty": current_booking.faculty.username,
                        "batch": current_booking.batch.name,
                        "start_time": current_booking.start_time.isoformat(),
                        "end_time": current_booking.end_time.isoformat()
                    } if current_booking else None
                }
            })

            classroom_list.append(classroom_obj)

        # Sort classrooms: available rooms first, then by free time
        classroom_list.sort(key=lambda x: (not x['available'], x['freeTime']))

        if not classroom_list:
            return Response(
                base_error_response("No classrooms found"),
                status=status.HTTP_200_OK
            )
            
        return Response(
            base_success_response("Classroom list retrieved successfully", classroom_list),
            status=status.HTTP_200_OK
        )