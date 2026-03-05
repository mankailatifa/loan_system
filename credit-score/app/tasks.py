import os
import time
from celery import Celery
from .database import SessionLocal, LoanRequestDB

RABBITMQ_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")

# Initialisation du worker Celery
app = Celery("credit_tasks", broker=RABBITMQ_URL)

@app.task(name="credit.evaluate_score")
def evaluate_score(request_id, monthly_income, monthly_expenses):
    print(f"Démarrage de l'analyse de crédit pour le dossier {request_id}...")
    
    # Simulation d'un appel API externe long (ex: Banque de France)
    time.sleep(5) 

    # --- Logique Métier (Formule du README) ---
    debt = monthly_expenses * 12
    late_payments = 0
    has_bankruptcy = False

    score = 1000 - (0.1 * debt) - (50 * late_payments) - (200 if has_bankruptcy else 0)
    score = max(0, min(1000, score))
    # ------------------------------------------

    # Mise à jour dans la base de données PostgreSQL
    db = SessionLocal()
    try:
        loan = db.query(LoanRequestDB).filter(LoanRequestDB.id == request_id).first()
        if loan:
            loan.credit_score = score
            db.commit()
            print(f"✅ Score calculé pour {request_id} : {score}/1000")
            
            app.send_task('notification.send_email', args=[request_id, loan.client_name, "CREDIT_DONE"], queue='notification_queue')
    finally:
        db.close()
    
    # --- NOUVEAU : Vérification pour la Décision Finale ---
    db_check = SessionLocal()
    try:
        check_loan = db_check.query(LoanRequestDB).filter(LoanRequestDB.id == request_id).first()
        # On vérifie si l'immo a AUSSI fini son travail
        if check_loan and check_loan.credit_score is not None and check_loan.property_value is not None:
            print("➡️ Le Crédit est le dernier à finir ! Envoi à la décision finale...")
            app.send_task('decision.evaluate_solvency', args=[request_id], queue='decision_queue')
        
    finally:
        db_check.close()
        
    return {"request_id": request_id, "score": score}