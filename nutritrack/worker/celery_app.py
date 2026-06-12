from celery import Celery
from nutritrack.api.settings import get_settings

settings = get_settings()

celery_app = Celery(
    "nutritrack",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["nutritrack.worker.tasks"],
    broker_connection_retry_on_startup=True,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)
