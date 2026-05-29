from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from .database import get_session
from .models import Person
from .schemas import PersonCreate, PersonRead
from .auth import get_current_user

router = APIRouter(prefix="/api/people", tags=["people"])

@router.post("/", response_model=PersonRead, dependencies=[Depends(get_current_user)])
def create_person(person: PersonCreate, session: Session = Depends(get_session)):
    """Create a new person/debtor record"""
    db_person = Person.from_orm(person)
    session.add(db_person)
    session.commit()
    session.refresh(db_person)
    return db_person

@router.get("/", response_model=List[PersonRead], dependencies=[Depends(get_current_user)])
def list_people(session: Session = Depends(get_session), skip: int = 0, limit: int = 100):
    """List all people/debtors"""
    people = session.exec(select(Person).offset(skip).limit(limit)).all()
    return people

@router.get("/{person_id}", response_model=PersonRead, dependencies=[Depends(get_current_user)])
def get_person(person_id: int, session: Session = Depends(get_session)):
    """Get a specific person by ID"""
    person = session.get(Person, person_id)
    if not person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    return person

@router.put("/{person_id}", response_model=PersonRead, dependencies=[Depends(get_current_user)])
def update_person(person_id: int, person_update: PersonCreate, session: Session = Depends(get_session)):
    """Update a person's information"""
    db_person = session.get(Person, person_id)
    if not db_person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    
    person_data = person_update.dict(exclude_unset=True)
    for key, value in person_data.items():
        setattr(db_person, key, value)
    
    session.add(db_person)
    session.commit()
    session.refresh(db_person)
    return db_person

@router.delete("/{person_id}", dependencies=[Depends(get_current_user)])
def delete_person(person_id: int, session: Session = Depends(get_session)):
    """Delete a person record"""
    db_person = session.get(Person, person_id)
    if not db_person:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Person not found")
    
    session.delete(db_person)
    session.commit()
    return {"deleted": True}