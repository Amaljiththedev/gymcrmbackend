
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

# ✅ This ensures all tasks in `tasks.py` across installed apps are auto-discovered
app.autodiscover_tasks()