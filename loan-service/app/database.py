import os
from sqlalchemy import create_engine, Column, String, Float,Boolean
from sqlalchemy.orm import declarative_base, sessionmaker

# L'URL de la base de données vient de Kubernetes/Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/loan_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Voici la table qui va stocker les données du formulaire
class LoanRequestDB(Base):
    __tablename__ = "loan_requests"

    # Informations de base (remplies par le formulaire)
    id = Column(String, primary_key=True, index=True)
    client_name = Column(String)
    monthly_income = Column(Float)
    monthly_expenses = Column(Float)
    loan_amount = Column(Float)
    property_address = Column(String)
    status = Column(String, default="PENDING")

    # Informations ajoutées par le worker Credit
    credit_score = Column(Float, nullable=True)

    # Informations ajoutées par le worker Property
    property_value = Column(Float, nullable=True)
    is_property_valid = Column(Boolean, nullable=True)
    notification_sent = Column(Boolean, default=False)


# Crée les tables dans la base de données
Base.metadata.create_all(bind=engine)