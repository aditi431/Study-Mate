from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.db.models import Note
from app.schemas.note import NoteCreate, NoteUpdate


def list_notes(db: Session, user_id: str) -> list[Note]:
    return list(
        db.scalars(
            select(Note)
            .where(Note.user_id == user_id)
            .order_by(Note.created_at.desc(), Note.id.desc())
        )
    )


def search_notes(db: Session, user_id: str, query: str) -> list[Note]:
    pattern = f"%{query}%"
    return list(
        db.scalars(
            select(Note)
            .where(
                Note.user_id == user_id,
                or_(Note.title.ilike(pattern), Note.description.ilike(pattern)),
            )
            .order_by(Note.created_at.desc(), Note.id.desc())
        )
    )


def create_note(db: Session, user_id: str, data: NoteCreate) -> Note:
    note = Note(user_id=user_id, **data.model_dump())
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


def update_note(
    db: Session, user_id: str, note_id: str, data: NoteUpdate
) -> Note | None:
    note = db.scalar(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    if note is None:
        return None
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(note, key, value)
    db.commit()
    db.refresh(note)
    return note


def delete_note(db: Session, user_id: str, note_id: str) -> bool:
    note = db.scalar(
        select(Note).where(Note.id == note_id, Note.user_id == user_id)
    )
    if note is None:
        return False
    db.delete(note)
    db.commit()
    return True
