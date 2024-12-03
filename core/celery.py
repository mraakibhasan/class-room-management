import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')

# Configure Celery Beat settings
app.conf.update(
    broker_connection_retry_on_startup=True,
    beat_scheduler='django_celery_beat.schedulers:DatabaseScheduler',
    beat_max_loop_interval=300,  # 5 minutes
)

# Load tasks from all registered apps
app.autodiscover_tasks()

# Configure periodic tasks
app.conf.beat_schedule = {
    'cleanup-old-bookings': {
        'task': 'apps.classroom.tasks.cleanup_old_bookings',
        'schedule': crontab(minute='*/15'),
    },
}