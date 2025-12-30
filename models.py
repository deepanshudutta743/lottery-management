from sqlalchemy import Column, Integer, String
from database import Base

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    numbers = Column(String)
    user_name = Column(String)
