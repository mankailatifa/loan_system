from celery import Celery
import os

# On récupère l'URL de RabbitMQ depuis les variables d'environnement (défini dans Kubernetes/Docker)
RABBITMQ_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@localhost:5672//")

celery_client = Celery(
    "loan_tasks",
    broker=RABBITMQ_URL
)

celery_client.conf.task_routes = {
    'credit.evaluate_score': {'queue': 'credit_queue'},
    'property.evaluate_value': {'queue': 'property_queue'}
}