"""
This module configures and initializes a Celery application.

The Celery app, named `statistic`, is configured with a broker and backend
defined using the application settings. It is tailored for distributed task
management with a JSON-based serialization protocol to ensure consistency
and reliability.

Configuration Details:
- **Broker**: RabbitMQ (URL fetched from `settings.celery_broker_url`) is
 used to manage task queues.
- **Backend**: Redis (URL fetched from `settings.celery_backend_url`) is
 used for storing task results.
- **Task Annotations**: Global rate-limiting of tasks at 10 tasks
 per minute.
- **Serialization**: Tasks and results are serialized and deserialized
 using JSON.
- **Retry on Startup**: Celery retries connections with the broker during
 startup if the broker is unavailable.
- **Result Expiry**: Task results are retained for 1 hour (3600 seconds)
 before expiration.

Exports:
    app (Celery): An initialized Celery application, ready for task
    scheduling and execution within the application ecosystem.
"""
from celery import Celery

from core.base_settings import settings

RESULT_EXPIRES: int = 3600

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
    result_expires=RESULT_EXPIRES,
)
