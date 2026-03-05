import os
import time
import random
from celery import Celery
from .database import SessionLocal, LoanRequestDB

RABBITMQ_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")

app = Celery("property_tasks", broker=RABBITMQ_URL)

@app.task(name="property.evaluate_value")
def evaluate_value(request_id, property_address, loan_amount):
    print(f"🏠 Démarrage de l'estimation pour le bien situé à : {property_address}...")
    
    # Simulation du temps de traitement (API externe immobilière) 
    time.sleep(6) 
    
    # --- Logique Métier ---
    estimated_value = loan_amount * random.uniform(0.8, 1.5)
    is_valid = loan_amount <= (estimated_value * 0.95)
    # ----------------------

    # Mise à jour dans la base de données PostgreSQL
    db = SessionLocal()
    try:
        loan = db.query(LoanRequestDB).filter(LoanRequestDB.id == request_id).first()
        if loan:
            loan.property_value = round(estimated_value, 2)
            loan.is_property_valid = is_valid
            db.commit()
            app.send_task('notification.send_email', args=[request_id, loan.client_name, "PROPERTY_DONE"], queue='notification_queue')
            statut = "✅ VALIDE" if is_valid else "❌ INVALIDE (Bien surévalué)"
            print(f"🏡 Résultat pour {request_id} : Valeur estimée = {loan.property_value}€ -> {statut}")
    finally:
        db.close()
    
    # --- NOUVEAU : Vérification pour la Décision Finale ---
    db_check = SessionLocal()
    try:
        check_loan = db_check.query(LoanRequestDB).filter(LoanRequestDB.id == request_id).first()
        # On vérifie si le crédit a AUSSI fini son travail
        if check_loan and check_loan.credit_score is not None and check_loan.property_value is not None:
            print("➡️ L'Immo est le dernier à finir ! Envoi à la décision finale...")
            app.send_task('decision.evaluate_solvency', args=[request_id], queue='decision_queue')
    finally:
        db_check.close()
        
    return {"request_id": request_id, "estimated_value": estimated_value, "is_valid": is_valid}