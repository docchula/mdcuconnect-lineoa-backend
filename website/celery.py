import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")


app = Celery("website")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.worker_hijack_root_logger = False
app.autodiscover_tasks()
