from collections.abc import Generator
from typing import Annotated
import uuid

import pytest
from fastapi import Depends, Header, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.dependencies import get_current_user, get_user_db
from app.db.models import Base, Profile
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
                Profile(id=USER_ONE, email="one@example.test"),
                Profile(id=USER_TWO, email="two@example.test"),
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
        return {"id": user_id}

    def test_db(
        user: Annotated[dict, Depends(test_auth_user)],
    ) -> Generator[Session, None, None]:
        with factory() as session:
            yield session

    app.dependency_overrides[get_current_user] = test_auth_user
    app.dependency_overrides[get_user_db] = test_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def auth_headers():
    return {
        "one": {"Authorization": f"Bearer {USER_ONE}"},
        "two": {"Authorization": f"Bearer {USER_TWO}"},
    }
