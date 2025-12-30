from pydantic import BaseModel
from typing import List

class TicketCreate(BaseModel):
    user_name: str

class TicketResponse(BaseModel):
    ticket_id: int
    numbers: List[int]
