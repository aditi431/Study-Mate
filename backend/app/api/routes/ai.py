"""Local AI prototype endpoints backed by the StudyMate knowledge service."""
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_user_db
from app.db.models import ChatMessage, ChatSession, Note
from app.services.ai import generate_ai_answer
router = APIRouter(prefix="/ai", tags=["AI"], dependencies=[Depends(get_current_user)])


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)
    mode: Literal["simple", "example", "quiz"] = "simple"
    session_id: str | None = None


class AskResponse(BaseModel):
    answer: str
    session_id: str
    topic_detected: str
    sources: list[str]


class SessionMessage(BaseModel):
    id: str
    role: str
    content: str
    mode: str | None
    created_at: str


class ChatSessionResponse(BaseModel):
    id: str
    messages: list[SessionMessage]


@router.post("/ask", response_model=AskResponse)
def ask_question(
    body: AskRequest,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_user_db)],
) -> AskResponse:
    session = None
    if body.session_id:
        session = db.scalar(
            select(ChatSession).where(
                ChatSession.id == body.session_id,
                ChatSession.user_id == user["id"],
            )
        )
        if session is None:
            raise HTTPException(status_code=404, detail="Chat session not found.")
    else:
        session = ChatSession(user_id=user["id"])
        db.add(session)
        db.flush()

    db.add(
        ChatMessage(
            session_id=session.id,
            role="user",
            content=body.question,
            mode=body.mode,
        )
    )

    notes = list(
        db.scalars(
            select(Note)
            .where(Note.user_id == user["id"])
            .order_by(Note.created_at.desc())
            .limit(20)
        )
    )
    note_context = [
        f"{note.title}: {note.description}"
        for note in notes
    ]
    generated = generate_ai_answer(body.question, body.mode, note_context)

    db.add(
        ChatMessage(
            session_id=session.id,
            role="assistant",
            content=generated["answer"],
            mode=body.mode,
        )
    )
    db.commit()

    return AskResponse(
        answer=generated["answer"],
        session_id=session.id,
        topic_detected=generated["topic_detected"],
        sources=generated["sources"],
    )


@router.get("/sessions", response_model=list[dict])
def list_sessions(
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_user_db)],
) -> list[dict]:
    sessions = list(
        db.scalars(
            select(ChatSession)
            .where(ChatSession.user_id == user["id"])
            .order_by(ChatSession.created_at.desc())
            .limit(20)
        )
    )
    result = []
    for session in sessions:
        msgs = list(
            db.scalars(
                select(ChatMessage)
                .where(ChatMessage.session_id == session.id)
                .order_by(ChatMessage.created_at)
                .limit(2)
            )
        )
        message_count = db.scalar(
            select(func.count(ChatMessage.id))
            .where(ChatMessage.session_id == session.id)
        ) or 0
        first_question = next((m.content for m in msgs if m.role == "user"), "New chat")
        result.append({
            "id": session.id,
            "preview": first_question[:60] + ("..." if len(first_question) > 60 else ""),
            "created_at": session.created_at.isoformat(),
            "message_count": message_count,
        })
    return result


@router.get("/sessions/{session_id}", response_model=ChatSessionResponse)
def get_session(
    session_id: str,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_user_db)],
) -> ChatSessionResponse:
    from fastapi import HTTPException
    session = db.scalar(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user["id"],
        )
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    messages = list(
        db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at)
        )
    )
    return ChatSessionResponse(
        id=session.id,
        messages=[
            SessionMessage(
                id=m.id,
                role=m.role,
                content=m.content,
                mode=m.mode,
                created_at=m.created_at.isoformat(),
            )
            for m in messages
        ],
    )


@router.delete("/sessions/{session_id}", status_code=204)
def delete_session(
    session_id: str,
    user: Annotated[dict, Depends(get_current_user)],
    db: Annotated[Session, Depends(get_user_db)],
) -> None:
    from fastapi import HTTPException, Response
    session = db.scalar(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == user["id"],
        )
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    db.delete(session)
    db.commit()
