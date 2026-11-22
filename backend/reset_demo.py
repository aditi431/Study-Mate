from app.config import get_settings
from app.db.database import get_session_factory
from app.services.demo import seed_demo_data


def main() -> None:
    settings = get_settings()
    if not settings.demo_mode:
        raise RuntimeError("Set DEMO_MODE=true before resetting demo data.")

    with get_session_factory()() as db:
        seed_demo_data(db, settings, reset=True)
    print("Demo notes and chat history have been reset.")


if __name__ == "__main__":
    main()
