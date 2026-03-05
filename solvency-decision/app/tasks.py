import os
from celery import Celery
from .database import SessionLocal, LoanRequestDB

RABBITMQ_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")

app = Celery("decision_tasks", broker=RABBITMQ_URL)

@app.task(name="decision.evaluate_solvency")
def evaluate_solvency(request_id):
    print(f"⚖️ Démarrage de la décision finale pour le dossier {request_id}...")
    
    db = SessionLocal()
    final_status = "PENDING"
    
    try:
        loan = db.query(LoanRequestDB).filter(LoanRequestDB.id == request_id).first()
        
        if not loan:
            print(f"❌ Dossier {request_id} introuvable.")
            return {"request_id": request_id, "status": "NOT_FOUND"}
            
        # Règles d'approbation (Exemple métier) :
        # 1. Le score de crédit doit être supérieur à 600
        # 2. L'évaluation du bien doit être valide
        # 3. Le taux d'endettement (dépenses / revenus) ne doit pas dépasser 35%
        
        taux_endettement = (loan.monthly_expenses / loan.monthly_income) * 100 if loan.monthly_income > 0 else 100
        
        is_approved = (
            loan.credit_score is not None and loan.credit_score >= 600 and
            loan.is_property_valid is True and
            taux_endettement <= 35
        )
        
        # L'indentation est maintenant parfaitement alignée :
        loan.status = "APPROVED" if is_approved else "REJECTED"
        final_status = loan.status  # On sauvegarde le statut pour le return final
        db.commit()
        
        print(f"🏁 Décision pour {request_id} : {loan.status}")
        
        # On déclenche l'envoi de l'email !
        app.send_task(
            'notification.send_email', 
            args=[request_id, loan.client_name, loan.status], # On envoie le statut final
            queue='notification_queue'
        )
        
    finally:
        db.close()
        
    return {"request_id": request_id, "status": final_status}