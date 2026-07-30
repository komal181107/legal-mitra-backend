from app.database import Base, engine
from app.models import User, ChatHistory, Conversation
from fastapi import FastAPI
from app.routers.chat import router as chat_router
from app.routers.auth import router as auth_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Legal Mitra API",
    description="AI Legal Assistant Backend",
    version="1.0.0"
)

app.include_router(chat_router)
app.include_router(auth_router)

@app.get("/")
def home():
    return {
        "status": "success",
        "message": "Welcome to Legal Mitra"
    }