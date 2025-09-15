from celery import Celery

celery = Celery(
    "yapp",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)


celery.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=True,
)
