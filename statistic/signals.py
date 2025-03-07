from celery.signals import task_failure

from core.logger_configuration import app_logger


@task_failure.connect
def task_failure_handler(
    sender=None, task_id=None, args=None, kwargs=None, einfo=None, **_
) -> None:
    app_logger.error(f"Task {sender.name if sender else 'unknown task'}"
                     f" with id {task_id} failed. Args: {args}, Kwargs:"
                     f" {kwargs}, Exception: {einfo}"
)