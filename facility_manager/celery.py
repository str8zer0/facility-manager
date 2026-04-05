import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "facility_manager.settings.dev")


app = Celery("facility_manager")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
