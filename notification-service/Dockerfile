FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app/app
# Écoute la file "notification_queue"
CMD ["celery", "-A", "app.tasks", "worker", "-Q", "notification_queue", "--loglevel=info"]