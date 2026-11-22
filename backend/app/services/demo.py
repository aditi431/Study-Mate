from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.config import Settings
from app.db.models import ChatSession, Note, User
from app.services.auth import hash_password

DEMO_USER_ID = "00000000-0000-4000-8000-000000000001"

_SAMPLE_NOTES = (
    (
        "Photosynthesis",
        "Plants use light, water, and carbon dioxide to produce glucose and oxygen.",
        3,
    ),
    (
        "React state",
        "State stores values that change over time and cause a component to re-render.",
        2,
    ),
    (
        "Water cycle",
        "Evaporation, condensation, precipitation, and collection move water through the environment.",
        4,
    ),
)


def seed_demo_data(db: Session, settings: Settings, *, reset: bool = False) -> None:
    if not settings.demo_mode or settings.demo_password is None:
        raise RuntimeError("Demo seeding requires DEMO_MODE=true and DEMO_PASSWORD.")

    demo_email = settings.demo_email.strip().lower()
    user = db.get(User, DEMO_USER_ID)
    owner = db.scalar(select(User).where(User.email == demo_email))

    if owner is not None and owner.id != DEMO_USER_ID:
        raise RuntimeError(
            "DEMO_EMAIL already belongs to a non-demo account. Choose a different DEMO_EMAIL."
        )
    if user is not None and user.email != demo_email:
        raise RuntimeError(
            "The seeded demo account does not match DEMO_EMAIL. Restore its original email "
            "or reset the demo account explicitly."
        )

    try:
        if user is None:
            user = User(
                id=DEMO_USER_ID,
                email=demo_email,
                name="StudyMate Demo",
                hashed_password=hash_password(settings.demo_password.get_secret_value()),
            )
            db.add(user)
        else:
            user.hashed_password = hash_password(settings.demo_password.get_secret_value())

        if reset:
            sessions = db.scalars(
                select(ChatSession).where(ChatSession.user_id == DEMO_USER_ID)
            )
            for chat_session in sessions:
                db.delete(chat_session)
            db.execute(delete(Note).where(Note.user_id == DEMO_USER_ID))
            db.flush()

        has_notes = db.scalar(
            select(Note.id).where(Note.user_id == DEMO_USER_ID).limit(1)
        )
        if reset or has_notes is None:
            for title, description, topics_count in _SAMPLE_NOTES:
                db.add(
                    Note(
                        user_id=DEMO_USER_ID,
                        title=title,
                        description=description,
                        topics_count=topics_count,
                    )
                )
        db.commit()
    except Exception:
        db.rollback()
        raise
