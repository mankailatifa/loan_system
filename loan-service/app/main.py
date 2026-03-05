from fastapi import FastAPI, Depends, Request, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, LoanRequestDB
from .celery_app import celery_client
import uuid
import asyncio

app = FastAPI(title="BankFlow API")

templates = Jinja2Templates(directory="app/templates")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 1. Affichage de la page Web (Dashboard SPA)
@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 2. NOUVEAU : API pour récupérer l'historique de tous les dossiers
@app.get("/api/loans")
def get_all_loans(db: Session = Depends(get_db)):
    # On récupère tous les dossiers dans la base de données
    loans = db.query(LoanRequestDB).all()
    
    # On formate les données pour le front-end (on inverse la liste pour avoir les plus récents en haut)
    result = []
    for loan in reversed(loans):
        result.append({
            "id": loan.id,
            "client_name": loan.client_name,
            "loan_amount": loan.loan_amount,
            "status": loan.status
        })
    return result

# 3. Soumission d'un nouveau dossier
@app.post("/submit-form/")
def submit_form(
    client_name: str = Form(...),
    monthly_income: float = Form(...),
    monthly_expenses: float = Form(...),
    loan_amount: float = Form(...),
    property_address: str = Form(...),
    db: Session = Depends(get_db)
):
    request_id = str(uuid.uuid4())
    
    new_loan = LoanRequestDB(
        id=request_id,
        client_name=client_name,
        monthly_income=monthly_income,
        monthly_expenses=monthly_expenses,
        loan_amount=loan_amount,
        property_address=property_address,
        status="PENDING"
    )
    db.add(new_loan)
    db.commit()

    # Envoi aux workers
    celery_client.send_task('credit.evaluate_score', args=[request_id, monthly_income, monthly_expenses], queue='credit_queue')
    celery_client.send_task('property.evaluate_value', args=[request_id, property_address, loan_amount], queue='property_queue')

    return {"message": "Dossier créé avec succès !", "id_suivi": request_id}

# 4. WebSocket pour le suivi en Temps Réel
@app.websocket("/ws/notifications/{request_id}")
async def websocket_endpoint(websocket: WebSocket, request_id: str):
    await websocket.accept()
    try:
        last_state = None
        while True:
            db = SessionLocal()
            loan = db.query(LoanRequestDB).filter(LoanRequestDB.id == request_id).first()
            if not loan:
                db.close()
                await asyncio.sleep(1)
                continue
                
            # MISE À JOUR : On ajoute notification_sent ici
            current_state = {
                "request_id": request_id,
                "status": loan.status,
                "credit_done": loan.credit_score is not None,
                "property_done": loan.property_value is not None,
                "notification_sent": getattr(loan, 'notification_sent', False) # Sécurité si pas encore migré
            }
            db.close()
            
            if current_state != last_state:
                await websocket.send_json(current_state)
                last_state = current_state
                
            # MISE À JOUR : On ne coupe la connexion QUE quand la notification est confirmée
            if current_state["notification_sent"]:
                break
                
            await asyncio.sleep(1)
            
    except WebSocketDisconnect:
        print(f"Client déconnecté pour le suivi du dossier {request_id}")
    except Exception as e:
        print(f"Erreur WebSocket: {e}")