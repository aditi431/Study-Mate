from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_user_db
from app.schemas.note import NoteCreate, NoteResponse, NoteUpdate
from app.services import notes as note_service

router = APIRouter(prefix="/notes", tags=["notes"])


@router.get("", response_model=list[NoteResponse])
def list_notes(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_user_db)],
) -> list[NoteResponse]:
    return note_service.list_notes(db, user["id"])


@router.get("/search", response_model=list[NoteResponse])
def search_notes(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_user_db)],
    q: Annotated[str, Query(min_length=1, max_length=200)],
) -> list[NoteResponse]:
    query = q.strip()
    if not query:
        raise HTTPException(status_code=422, detail="Search query must not be blank.")
    return note_service.search_notes(db, user["id"], query)


@router.post("", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
def create_note(
    data: NoteCreate,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_user_db)],
) -> NoteResponse:
    return note_service.create_note(db, user["id"], data)


@router.patch("/{note_id}", response_model=NoteResponse)
def update_note(
    note_id: str,
    data: NoteUpdate,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_user_db)],
) -> NoteResponse:
    note = note_service.update_note(db, user["id"], note_id, data)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found.")
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: str,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_user_db)],
) -> Response:
    if not note_service.delete_note(db, user["id"], note_id):
        raise HTTPException(status_code=404, detail="Note not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
