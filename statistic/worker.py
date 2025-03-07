from celery import Celery

import statistic.signals
from core.base_settings import settings

app = Celery("statistic",
             broker=f"amqp://{settings.RABBIT_USER}:{settings.RABBIT_PASSWORD}@rabbitmq:5672//",
             backend="rpc://",
             # task_cls="celery_asyncio.task:AsyncTask"
             )

app.conf.update(
    task_annotations={"*": {"rate_limit": "10/m"}},
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    broker_connection_retry_on_startup=True

)
