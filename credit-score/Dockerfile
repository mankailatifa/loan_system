FROM python:3.11-slim

WORKDIR /app

# Copier les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le package app
COPY ./app ./app

# Définir PYTHONPATH pour que Python trouve le package app
ENV PYTHONPATH=/app

# Commande par défaut pour Celery worker
CMD ["celery", "-A", "app.celery_app", "worker", "--loglevel=info"]
