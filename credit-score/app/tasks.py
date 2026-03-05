from celery import Celery
from sqlalchemy import create_engine, text

# Création de l'instance Celery
celery_app = Celery(
    "credit_tasks",
    broker="pyamqp://guest@rabbitmq//",
    backend="redis://redis:6379/0"
)

# DB financière
FINANCE_DB = "postgresql://finance_user:finance_pass@postgres:5432/finance_db"
LOAN_DB = "postgresql://loan_user:loan_pass@postgres:5432/loan_db"

finance_engine = create_engine(FINANCE_DB)
loan_engine = create_engine(LOAN_DB)

# Tâche enregistrée avec le nom exact
@celery_app.task(name="compute_credit_score")
def compute_credit_score(client_id):
    # récupération des infos financières
    with finance_engine.connect() as conn:
        result = conn.execute(
            text("SELECT debt, late_payments, has_bankruptcy FROM financial_info WHERE client_id = :client_id"),
            {"client_id": client_id}
        ).fetchone()

    if not result:
        print("Client not found")
        return None

    debt = result.debt
    late_payments = result.late_payments
    has_bankruptcy = result.has_bankruptcy

    # calcul du score
    score = 1000 - 0.1*debt - 50*late_payments - (200 if has_bankruptcy else 0)

    # mise à jour dans loans
    with loan_engine.connect() as conn:
        conn.execute(
            text("UPDATE loans SET credit_score = :score WHERE client_id = :client_id"),
            {"score": score, "client_id": client_id}
        )
        conn.commit()

    print(f"Score for {client_id}: {score}")
    return score
