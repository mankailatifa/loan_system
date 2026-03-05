from celery import Celery

celery_app = Celery(
    "loan_tasks",
    broker="pyamqp://guest@rabbitmq//",
    backend="redis://redis:6379/0"
)

celery_app.send_task("compute_credit_score", args=["C001"])
