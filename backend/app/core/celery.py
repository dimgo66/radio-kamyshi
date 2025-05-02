from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

celery_app.conf.task_routes = {
    "app.tasks.broadcaster.*": {"queue": "broadcast-queue"},
    "app.tasks.track_processing.*": {"queue": "media-queue"},
}

celery_app.conf.imports = [
    "app.tasks.broadcaster",
    "app.tasks.track_processing",
]

# Настройка периодических задач
celery_app.conf.beat_schedule = {
    "check-scheduled-programs": {
        "task": "app.tasks.broadcaster.check_scheduled_programs",
        "schedule": 60.0,  # каждую минуту
    },
    "cleanup-old-programs": {
        "task": "app.tasks.broadcaster.cleanup_old_programs",
        "schedule": crontab(hour=3, minute=0),  # каждый день в 3:00
    },
} 