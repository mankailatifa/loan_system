from celery import Celery

celery_app = Celery(
    "credit_score",
    broker="pyamqp://guest@rabbitmq//",  # doit être le même broker que loan-service
    backend="redis://redis:6379/0"       # ou autre backend si tu veux récupérer le résultat
)

celery_app.autodiscover_tasks(["app.tasks"])
