from collections.abc import Generator
from typing import Annotated, Any

import jwt as pyjwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.database import get_db
from app.services.auth import decode_access_token

_bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials | None, Depends(_bearer_scheme)
    ],
) -> dict[str, Any]:
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please sign in.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = credentials.credentials
    try:
        claims = decode_access_token(token)
        user_id = claims["sub"]
        email = claims.get("email", "")
    except pyjwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired. Please sign in again.")
    except pyjwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail="Invalid access token.") from exc
    return {"id": user_id, "email": email}


def get_user_db(
    db: Annotated[Session, Depends(get_db)],
) -> Generator[Session, None, None]:
    yield db
