import os
import time
from celery import Celery
from .database import SessionLocal, LoanRequestDB

RABBITMQ_URL = os.getenv("CELERY_BROKER_URL", "amqp://guest:guest@rabbitmq:5672//")
app = Celery("notification_tasks", broker=RABBITMQ_URL)

@app.task(name="notification.send_email")
def send_email(request_id, client_name, step_or_status):
    print(f"📧 [NOTIFICATION] Envoi d'un message à {client_name} pour : {step_or_status}")
    
    if step_or_status == "CREDIT_DONE":
        print(f"✅ EMAIL : Votre analyse de crédit est terminée.")
    elif step_or_status == "PROPERTY_DONE":
        print(f"🏠 EMAIL : L'estimation de votre bien est terminée.")
    elif step_or_status in ["APPROVED", "REJECTED"]:
        print(f"🏁 EMAIL : Décision finale -> {step_or_status}")
        
        # On valide la notification en base UNIQUEMENT pour la décision finale
        # (C'est ce qui indique à l'interface web que tout le processus est fini)
        db = SessionLocal()
        try:
            loan = db.query(LoanRequestDB).filter(LoanRequestDB.id == request_id).first()
            if loan:
                loan.notification_sent = True
                db.commit()
        finally:
            db.close()
            
    return {"request_id": request_id, "step": step_or_status}