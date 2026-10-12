from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.ai import router as ai_router
from app.api.routes.auth import router as auth_router
from app.api.routes.notes import router as notes_router
from app.api.routes.health import router as health_router
from app.config import get_settings
from app.db.database import get_engine

settings = get_settings()

# Initialize DB on startup
get_engine()

app = FastAPI(
    title=settings.app_name,
    description="Backend API for the StudyMate learning workspace.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(health_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(notes_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
