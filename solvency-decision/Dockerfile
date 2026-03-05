FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ./app /app/app

# Il écoutera la file "decision_queue"
CMD ["celery", "-A", "app.tasks", "worker", "-Q", "decision_queue", "--loglevel=info"]