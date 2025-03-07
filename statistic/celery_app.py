from celery import Celery

app = Celery("statistic",
             broker="amqp://",
             backend="rpc://",
             task_cls="celery_asyncio.task:AsyncTask"
             )

app.conf.update(
    task_annotations={"*": {"rate_limit": "10/m"}},
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
)
