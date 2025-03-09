from celery import Celery

from core.base_settings import settings

app = Celery(
    "statistic",
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_url,
)

app.conf.update(
    task_annotations={"*": {"rate_limit": "10/m"}},
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    broker_connection_retry_on_startup=True,
)
