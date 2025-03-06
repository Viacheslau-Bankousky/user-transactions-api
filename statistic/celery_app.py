from celery import Celery

app = Celery("statistic",
             broker="amqp://",
             backend="rpc://")