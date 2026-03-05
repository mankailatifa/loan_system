from fastapi import FastAPI
from app.tasks import compute_credit_score

app = FastAPI()

@app.get("/")
def home():
    return {"service": "credit-score-service"}

# endpoint pour lancer le calcul du score
@app.post("/compute-score/{client_id}")
def compute_score(client_id: str):

    task = compute_credit_score.delay(client_id)

    return {
        "message": "Score calculation started",
        "task_id": task.id
    }
