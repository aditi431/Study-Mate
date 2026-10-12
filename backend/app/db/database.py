from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import get_settings
from app.db.models import Base


@lru_cache
def get_engine():
    settings = get_settings()
    url = settings.database_url
    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False
    engine = create_engine(url, connect_args=connect_args, pool_pre_ping=True)
    # Create all tables automatically on first run
    Base.metadata.create_all(bind=engine)
    return engine


@lru_cache
def get_session_factory() -> sessionmaker[Session]:
    engine = get_engine()
    return sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    session_factory = get_session_factory()
    with session_factory() as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
