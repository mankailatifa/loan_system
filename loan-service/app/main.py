from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from sqlalchemy import create_engine, Column, Integer, String, Numeric
from sqlalchemy.orm import declarative_base, sessionmaker
from celery import Celery
# Import du task du microservice Credit-Score
#from app.tasks import compute_credit_score
from celery.result import AsyncResult
# from app.credit_tasks import compute_credit_score
# from app.celery_app import celery_app
from celery import Celery

celery_app = Celery(
    "loan_service",
    broker="pyamqp://guest@rabbitmq//"  # adresse de ton RabbitMQ
)

import os

app = FastAPI()

# -----------------------------
# Formulaire HTML
# -----------------------------

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FORM_PATH = os.path.join(BASE_DIR, "form.html")

@app.get("/form")
def get_form():
    if os.path.exists(FORM_PATH):
        return FileResponse(FORM_PATH)
    else:
        return {"error": "Form file not found"}

# -----------------------------
# Configuration PostgreSQL
# -----------------------------

DATABASE_URL = "postgresql://loan_user:loan_pass@postgres:5432/loan_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

# -----------------------------
# Modèle Loan
# -----------------------------

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String(50))
    client_name = Column(String(100))
    property_address = Column(String)
    property_value = Column(Numeric(15,2))
    loan_amount = Column(Numeric(15,2))
    loan_term_years = Column(Integer)

# création de la table
Base.metadata.create_all(bind=engine)

# -----------------------------
# Configuration Celery
# -----------------------------

celery_app = Celery(
    "loan_tasks",
    broker="pyamqp://guest@rabbitmq//"
)

# tâche envoyée au microservice credit
@celery_app.task
def compute_credit_score(client_id):
    print(f"Credit score requested for client {client_id}")

# -----------------------------
# Route pour créer un prêt
# -----------------------------

@app.post("/loans")
def create_loan(
    client_id: str = Form(...),
    client_name: str = Form(...),
    property_address: str = Form(...),
    property_value: float = Form(...),
    loan_amount: float = Form(...),
    loan_term_years: int = Form(...)
):

    db = SessionLocal()

    loan = Loan(
        client_id=client_id,
        client_name=client_name,
        property_address=property_address,
        property_value=property_value,
        loan_amount=loan_amount,
        loan_term_years=loan_term_years
    )

    # sauvegarder dans PostgreSQL
    db.add(loan)
    db.commit()
    db.refresh(loan)

    # envoyer la tâche au microservice credit
    # compute_credit_score.delay(client_id)
    # juste pour envoyer la tâche
    celery_app.send_task("compute_credit_score", args=[loan.client_id])
    db.close()

    return {
        "message": "Loan submitted successfully",
        "loan_id": loan.id
    }
