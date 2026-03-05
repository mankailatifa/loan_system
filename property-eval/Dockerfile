FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app/app

# On lance Celery en spécifiant la bonne file d'attente
CMD ["celery", "-A", "app.tasks", "worker", "-Q", "property_queue", "--loglevel=info"]