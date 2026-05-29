from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class PersonCreate(BaseModel):
    name: str
    phone: str
    email: str
    amount_owed: float
    sale_date: datetime
    state: str
    county: str

class PersonRead(PersonCreate):
    id: int

class CallLogRead(BaseModel):
    id: int
    person_id: int
    started_at: datetime
    call_sid: Optional[str]
    result: Optional[str]
    transcript: Optional[str]
    status: str

class EmailLogRead(BaseModel):
    id: int
    person_id: int
    direction: str
    subject: str
    body: str
    timestamp: datetime
    ai_summary: Optional[str]