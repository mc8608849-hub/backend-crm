from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from pydantic import BaseModel
from .database import get_session
from .models import CallLog, Person
from .schemas import CallLogRead
from .auth import get_current_user

router = APIRouter(prefix="/api/calls", tags=["calls"])

class CallLogCreate(BaseModel):
    person_id: int
    call_sid: Optional[str] = None
    status: str  # 'initiated', 'completed', 'failed', 'voicemail'

class CallLogUpdate(BaseModel):
    result: Optional[str] = None
    transcript: Optional[str] = None
    status: Optional[str] = None

@router.post("/", response_model=CallLogRead, dependencies=[Depends(get_current_user)])
def create_call_log(call: CallLogCreate, session: Session = Depends(get_session)):
    """Create a new call log entry"""
    # Verify person exists
    person = session.get(Person, call.person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    
    db_call = CallLog(
        person_id=call.person_id,
        call_sid=call.call_sid,
        status=call.status,
        started_at=datetime.utcnow()
    )
    session.add(db_call)
    session.commit()
    session.refresh(db_call)
    return db_call

@router.get("/", response_model=List[CallLogRead], dependencies=[Depends(get_current_user)])
def list_calls(session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    """List all call logs"""
    calls = session.exec(select(CallLog).offset(skip).limit(limit)).all()
    return calls

@router.get("/person/{person_id}", response_model=List[CallLogRead], dependencies=[Depends(get_current_user)])
def get_person_calls(person_id: int, session: Session = Depends(get_session)):
    """Get all calls for a specific person"""
    calls = session.exec(select(CallLog).where(CallLog.person_id == person_id)).all()
    return calls

@router.get("/{call_id}", response_model=CallLogRead, dependencies=[Depends(get_current_user)])
def get_call(call_id: int, session: Session = Depends(get_session)):
    """Get a specific call log"""
    call = session.get(CallLog, call_id)
    if not call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")
    return call

@router.put("/{call_id}", response_model=CallLogRead, dependencies=[Depends(get_current_user)])
def update_call_log(call_id: int, call_update: CallLogUpdate, session: Session = Depends(get_session)):
    """Update a call log with results and transcript"""
    db_call = session.get(CallLog, call_id)
    if not db_call:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Call not found")
    
    update_data = call_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_call, key, value)
    
    session.add(db_call)
    session.commit()
    session.refresh(db_call)
    return db_call