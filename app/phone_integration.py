"""
Phone Integration Module for Custom US Phone Numbers

This module provides utilities for integrating your own US phone number
with the CRM backend. It handles incoming calls, outgoing calls, and 
call logging.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlmodel import Session
from pydantic import BaseModel
import os
import json

from .database import get_session
from .models import CallLog, Person
from .auth import get_current_user

router = APIRouter(prefix="/api/phone", tags=["phone"])

# Schemas
class IncomingCallWebhook(BaseModel):
    """Webhook payload for incoming calls"""
    phone_number: str
    from_number: str
    call_id: str
    timestamp: str

class OutgoingCallRequest(BaseModel):
    """Request to make an outgoing call"""
    person_id: int
    message: str  # Message to be read via text-to-speech

class CallStatusUpdate(BaseModel):
    """Update call status"""
    call_id: str
    status: str  # 'ringing', 'answered', 'completed', 'failed', 'voicemail'
    transcript: Optional[str] = None
    duration: Optional[int] = None  # in seconds

# Phone Integration Configuration
CALLER_PHONE_NUMBER = os.getenv("CALLER_PHONE_NUMBER", "")
PHONE_WEBHOOK_SECRET = os.getenv("PHONE_WEBHOOK_SECRET", "")

@router.post("/incoming-webhook")
async def incoming_call_webhook(
    payload: IncomingCallWebhook,
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Webhook endpoint for receiving incoming call notifications.
    
    Your phone system should POST to this endpoint when a call comes in.
    
    Example with cURL:
    curl -X POST "http://localhost:8000/api/phone/incoming-webhook" \\
      -H "Content-Type: application/json" \\
      -d '{
        "phone_number": "+1555123456",
        "from_number": "+1234567890",
        "call_id": "call_12345",
        "timestamp": "2026-05-29T15:30:00Z"
      }'
    """
    
    # Verify webhook secret if configured
    if PHONE_WEBHOOK_SECRET:
        auth_header = request.headers.get("X-Webhook-Secret")
        if auth_header != PHONE_WEBHOOK_SECRET:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook secret"
            )
    
    try:
        # Find person by phone number
        from sqlmodel import select
        person = session.exec(
            select(Person).where(Person.phone == payload.from_number)
        ).first()
        
        if not person:
            # Log call even if person not found
            print(f"Incoming call from unknown number: {payload.from_number}")
            return {
                "status": "received",
                "message": "Call logged but person not found in database"
            }
        
        # Create call log entry
        call_log = CallLog(
            person_id=person.id,
            call_sid=payload.call_id,
            status="ringing",
            started_at=datetime.fromisoformat(payload.timestamp.replace("Z", "+00:00"))
        )
        session.add(call_log)
        session.commit()
        
        return {
            "status": "received",
            "message": "Call logged successfully",
            "call_log_id": call_log.id
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error processing webhook: {str(e)}"
        )

@router.post("/make-call", dependencies=[Depends(get_current_user)])
async def make_outgoing_call(
    call_request: OutgoingCallRequest,
    session: Session = Depends(get_session)
):
    """
    Initiate an outgoing call to a person.
    
    This endpoint:
    1. Fetches the person's phone number
    2. Creates a call log entry
    3. Sends the call instruction to your phone system
    
    Example:
    curl -X POST "http://localhost:8000/api/phone/make-call" \\
      -H "Authorization: Bearer YOUR_TOKEN" \\
      -H "Content-Type: application/json" \\
      -d '{
        "person_id": 1,
        "message": "Hello, this is a call from the CRM system."
      }'
    """
    
    # Get person
    person = session.get(Person, call_request.person_id)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found"
        )
    
    # Create call log
    call_log = CallLog(
        person_id=call_request.person_id,
        status="initiating",
        started_at=datetime.utcnow()
    )
    session.add(call_log)
    session.commit()
    session.refresh(call_log)
    
    # Here you would integrate with your phone system
    # Example: Send to your phone service provider's API
    phone_instruction = {
        "action": "make_call",
        "from_number": CALLER_PHONE_NUMBER,
        "to_number": person.phone,
        "message": call_request.message,
        "call_id": call_log.id,
        "callback_url": f"{os.getenv('API_URL', 'http://localhost:8000')}/api/phone/call-status-update"
    }
    
    # TODO: Send phone_instruction to your phone system
    # Example: requests.post("https://your-phone-provider.com/api/calls", json=phone_instruction)
    
    return {
        "status": "call_initiated",
        "call_log_id": call_log.id,
        "person_name": person.name,
        "phone_number": person.phone,
        "instruction": phone_instruction  # For debugging - remove in production
    }

@router.post("/call-status-update")
async def update_call_status(
    update: CallStatusUpdate,
    session: Session = Depends(get_session)
):
    """
    Webhook endpoint for call status updates.
    
    Your phone system should POST to this endpoint with call status updates.
    
    Example:
    curl -X POST "http://localhost:8000/api/phone/call-status-update" \\
      -H "Content-Type: application/json" \\
      -d '{
        "call_id": "call_123",
        "status": "completed",
        "transcript": "Customer agreed to payment plan",
        "duration": 245
      }'
    """
    
    from sqlmodel import select
    
    # Find call log by call_sid
    call_log = session.exec(
        select(CallLog).where(CallLog.call_sid == update.call_id)
    ).first()
    
    if not call_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Call not found"
        )
    
    # Update call log
    call_log.status = update.status
    if update.transcript:
        call_log.transcript = update.transcript
    if update.duration:
        call_log.result = f"Call duration: {update.duration} seconds"
    
    session.add(call_log)
    session.commit()
    
    return {
        "status": "updated",
        "call_id": update.call_id,
        "new_status": update.status
    }

@router.get("/stats", dependencies=[Depends(get_current_user)])
async def get_phone_stats(session: Session = Depends(get_session)):
    """
    Get phone call statistics
    """
    from sqlmodel import select, func
    
    total_calls = session.exec(select(func.count(CallLog.id))).first()
    completed_calls = session.exec(
        select(func.count(CallLog.id)).where(CallLog.status == "completed")
    ).first()
    failed_calls = session.exec(
        select(func.count(CallLog.id)).where(CallLog.status == "failed")
    ).first()
    
    return {
        "total_calls": total_calls or 0,
        "completed_calls": completed_calls or 0,
        "failed_calls": failed_calls or 0,
        "success_rate": (completed_calls or 0) / (total_calls or 1) * 100
    }
