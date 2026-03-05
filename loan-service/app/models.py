from sqlalchemy import Column, Integer, String, Float
from app.database import Base  # Base vient de database.py

class LoanRequest(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(String, index=True)
    client_name = Column(String)
    property_address = Column(String)
    property_value = Column(Float)
    loan_amount = Column(Float)
    loan_term_years = Column(Integer)
