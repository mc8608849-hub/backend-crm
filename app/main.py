from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .models import SQLModel
from .database import engine
from .ai_voice import router as ai_voice_router
from .auth import router as auth_router
from .person_router import router as person_router
from .ai_calls import router as ai_calls_router

app = FastAPI(title="CRM Backend", version="1.0.0")

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update to specific origins in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(bind=engine)

# Register routers
app.include_router(auth_router)
app.include_router(person_router)
app.include_router(ai_calls_router)
app.include_router(ai_voice_router)

@app.get("/")
def root():
    return {"message": "CRM Backend API", "docs": "/docs"}