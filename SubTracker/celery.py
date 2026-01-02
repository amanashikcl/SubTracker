import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SubTracker.settings')

# Ensure this says 'SubTracker', matching your folder name exactly
app = Celery('SubTracker')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()