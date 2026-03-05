FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

# Commande pour démarrer le Worker Celery en écoutant la BONNE file
CMD ["celery", "-A", "app.tasks", "worker", "-Q", "credit_queue", "--loglevel=info"]