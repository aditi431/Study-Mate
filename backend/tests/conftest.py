from collections.abc import Generator
import os
from typing import Annotated
import uuid

import pytest
from fastapi import Depends, Header, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["DATABASE_URL"] = "sqlite://"
os.environ["JWT_SECRET"] = "test-only-signing-key-with-at-least-32-characters"
os.environ["DEMO_MODE"] = "false"

from app.api.dependencies import get_current_user, get_user_db
from app.db.database import get_db
from app.db.models import Base, User
from app.main import app

USER_ONE = uuid.UUID("9bd852d2-1470-4b56-adb4-cdf0f12e2901")
USER_TWO = uuid.UUID("6381f88a-7fb7-4213-8bda-dfabecfc77ee")


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)
    with factory() as session:
        session.add_all(
            [
                User(id=str(USER_ONE), email="one@example.test", hashed_password="test"),
                User(id=str(USER_TWO), email="two@example.test", hashed_password="test"),
            ]
        )
        session.commit()

    def test_auth_user(
        authorization: Annotated[str | None, Header()] = None,
    ) -> dict[str, uuid.UUID]:
        if not authorization or not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing test bearer token.")
        try:
            user_id = uuid.UUID(authorization.removeprefix("Bearer "))
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Invalid test bearer token.") from exc
        return {"id": str(user_id)}

    def test_db(
        user: Annotated[dict, Depends(test_auth_user)],
    ) -> Generator[Session, None, None]:
        with factory() as session:
            yield session

    def test_db_unprotected() -> Generator[Session, None, None]:
        with factory() as session:
            yield session

    app.dependency_overrides[get_current_user] = test_auth_user
    app.dependency_overrides[get_db] = test_db_unprotected
    app.dependency_overrides[get_user_db] = test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def live_client() -> Generator[TestClient, None, None]:
    from app.api.limits import ai_limit_tracker

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    def test_db() -> Generator[Session, None, None]:
        with factory() as session:
            yield session

    app.dependency_overrides[get_db] = test_db
    app.dependency_overrides[get_user_db] = test_db
    app.dependency_overrides.pop(get_current_user, None)
    ai_limit_tracker.reset()
    app.state.test_session_factory = factory
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    ai_limit_tracker.reset()
    del app.state.test_session_factory
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def auth_headers():
    return {
        "one": {"Authorization": f"Bearer {USER_ONE}"},
        "two": {"Authorization": f"Bearer {USER_TWO}"},
    }
