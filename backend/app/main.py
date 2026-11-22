from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.ai import router as ai_router
from app.api.routes.auth import router as auth_router
from app.api.routes.health import router as health_router
from app.api.routes.notes import router as notes_router
from app.config import get_settings
from app.db.database import get_engine, get_session_factory
from app.services.demo import seed_demo_data

settings = get_settings()

# Create the tables before accepting requests.
get_engine()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if settings.demo_mode:
        session_factory = get_session_factory()
        with session_factory() as db:
            seed_demo_data(db, settings)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Backend API for the StudyMate learning workspace.",
    version="2.0.0",
    lifespan=lifespan,
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
