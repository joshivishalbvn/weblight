import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'weblight.settings')

app = Celery('weblight')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# celery -A weblight worker --loglevel=info
