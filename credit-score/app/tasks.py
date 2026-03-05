from celery import Celery
from sqlalchemy import create_engine, text

celery_app = Celery(
    "credit_tasks",
    broker="pyamqp://guest@rabbitmq//",
    backend="rpc://"
)

DATABASE_URL = "postgresql://finance_user:finance_pass@postgres:5432/finance_db"

engine = create_engine(DATABASE_URL)

@celery_app.task
def compute_credit_score(client_id):

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT debt, late_payments, has_bankruptcy
                FROM client_financials
                WHERE client_id = :client_id
            """),
            {"client_id": client_id}
        ).fetchone()

    if not result:
        print("Client not found")
        return None

    debt = result.debt
    late_payments = result.late_payments
    has_bankruptcy = result.has_bankruptcy

    score = 1000 - 0.1 * debt - 50 * late_payments

    if has_bankruptcy:
        score -= 200

    print(f"Client {client_id} score = {score}")

    return score
