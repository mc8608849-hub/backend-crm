import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from pydantic import BaseModel
from jose import JWTError, jwt
from passlib.context import CryptContext

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

router = APIRouter(prefix="/api/auth", tags=["auth"])

# Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Login(BaseModel):
    username: str
    password: str

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthCredentials = Depends(security)) -> str:
    """Verify JWT token and return username"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    return username

# Routes
@router.post("/login", response_model=Token)
def login(login_data: Login):
    """
    Login endpoint - verify credentials and return JWT token
    For now, using hardcoded credentials. Replace with DB lookup.
    """
    # TODO: Query database for user and verify password
    # This is a placeholder - implement proper user authentication
    
    VALID_USERNAME = os.getenv("AUTH_USERNAME", "admin")
    VALID_PASSWORD = os.getenv("AUTH_PASSWORD", "password")
    
    if login_data.username != VALID_USERNAME or login_data.password != VALID_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": login_data.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def get_current_user_info(current_user: str = Depends(get_current_user)):
    """Get current authenticated user info"""
    return {"username": current_user}