# app/worker.py
from app.tasks import celery_app  # <- important : toutes les tâches doivent être importées

if __name__ == "__main__":
    celery_app.worker_main(["worker", "--loglevel=info"])