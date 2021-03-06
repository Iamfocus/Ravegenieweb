from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

from dotenv import load_dotenv

load_dotenv('../.env')
app_env = os.getenv('APP_ENV', 'production')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'ravegenie.settings.{app_env}')

app = Celery('ravegenie')


app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
