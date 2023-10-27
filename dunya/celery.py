import os

from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dunya.settings')

app = Celery('dunya')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(settings.INSTALLED_APPS, related_name='jobs')
app.autodiscover_tasks(settings.INSTALLED_APPS, related_name='tasks')
