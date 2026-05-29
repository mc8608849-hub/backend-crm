import os
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
from sqlalchemy.orm import sessionmaker

# Database URL - adjust based on your needs
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///crm.db")

# Create engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=True
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=True,
        pool_pre_ping=True
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """Dependency for getting database session"""
    with Session(engine) as session:
        yield session