from fastapi.testclient import TestClient

from app.config import Settings
from app.db.models import User
from app.services.demo import DEMO_USER_ID, seed_demo_data


def test_health_is_available_without_authentication(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "StudyMate API"}


def test_notes_require_authentication(client: TestClient) -> None:
    response = client.get("/api/notes")

    assert response.status_code == 401


def test_create_list_search_update_and_delete_notes(client, auth_headers) -> None:
    created = client.post(
        "/api/notes",
        headers=auth_headers["one"],
        json={
            "title": "Biology",
            "description": "Cell structure and photosynthesis",
            "topics_count": 3,
            "user_id": "6381f88a-7fb7-4213-8bda-dfabecfc77ee",
        },
    )
    assert created.status_code == 422

    created = client.post(
        "/api/notes",
        headers=auth_headers["one"],
        json={
            "title": "Biology",
            "description": "Cell structure and photosynthesis",
            "topics_count": 3,
        },
    )
    assert created.status_code == 201
    note = created.json()
    assert note["title"] == "Biology"
    assert note["topics_count"] == 3
    assert note["id"]

    listed = client.get("/api/notes", headers=auth_headers["one"])
    assert [entry["id"] for entry in listed.json()] == [note["id"]]

    searched = client.get(
        "/api/notes/search",
        params={"q": "PHOTOSYNTHESIS"},
        headers=auth_headers["one"],
    )
    assert [entry["id"] for entry in searched.json()] == [note["id"]]

    updated = client.patch(
        f"/api/notes/{note['id']}",
        headers=auth_headers["one"],
        json={"title": "Cell Biology"},
    )
    assert updated.status_code == 200
    assert updated.json()["title"] == "Cell Biology"

    deleted = client.delete(
        f"/api/notes/{note['id']}", headers=auth_headers["one"]
    )
    assert deleted.status_code == 204
    assert client.get("/api/notes", headers=auth_headers["one"]).json() == []


def test_user_cannot_read_or_mutate_another_users_note(client, auth_headers) -> None:
    created = client.post(
        "/api/notes",
        headers=auth_headers["one"],
        json={"title": "Private", "description": "Only my account can see this"},
    )
    note_id = created.json()["id"]

    assert client.get("/api/notes", headers=auth_headers["two"]).json() == []
    assert client.patch(
        f"/api/notes/{note_id}",
        headers=auth_headers["two"],
        json={"title": "Stolen"},
    ).status_code == 404
    assert client.delete(
        f"/api/notes/{note_id}", headers=auth_headers["two"]
    ).status_code == 404

    original = client.get("/api/notes", headers=auth_headers["one"]).json()[0]
    assert original["title"] == "Private"


def test_note_validation(client, auth_headers) -> None:
    invalid = client.post(
        "/api/notes",
        headers=auth_headers["one"],
        json={"title": " ", "description": "text", "topics_count": -1},
    )
    assert invalid.status_code == 422


def test_registration_login_and_ai_chat(client) -> None:
    email = "reporter@example.com"
    registration = client.post(
        "/api/auth/register",
        json={"email": email, "password": "test1234", "name": "Reporter"},
    )
    assert registration.status_code == 201
    headers = {"Authorization": f"Bearer {registration.json()['user_id']}"}

    login = client.post(
        "/api/auth/login",
        json={"email": email, "password": "test1234"},
    )
    assert login.status_code == 200

    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["email"] == email

    first = client.post(
        "/api/ai/ask",
        headers=headers,
        json={"question": "Explain React state", "mode": "simple"},
    )
    assert first.status_code == 200
    assert first.json()["session_id"]
    assert "React" in first.json()["answer"]

    follow_up = client.post(
        "/api/ai/ask",
        headers=headers,
        json={
            "question": "Give me an example",
            "mode": "example",
            "session_id": first.json()["session_id"],
        },
    )
    assert follow_up.status_code == 200

    sessions = client.get("/api/ai/sessions", headers=headers)
    assert sessions.status_code == 200
    assert sessions.json()[0]["message_count"] == 4


def test_real_registration_login_and_authenticated_me(live_client: TestClient) -> None:
    registration = live_client.post(
        "/api/auth/register",
        json={"email": "real@example.com", "password": "secure-test-password", "name": "Real"},
    )
    assert registration.status_code == 201

    login = live_client.post(
        "/api/auth/login",
        json={"email": "real@example.com", "password": "secure-test-password"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    me = live_client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "real@example.com"


def test_ai_per_ip_limit_returns_friendly_429(live_client, monkeypatch) -> None:
    import app.api.routes.ai as ai_route

    settings = Settings(
        database_url="sqlite://",
        jwt_secret="test-only-signing-key-with-at-least-32-characters",
        ai_daily_limit_per_user=10,
        ai_rate_limit_per_minute=1,
    )
    monkeypatch.setattr(ai_route, "get_settings", lambda: settings)
    registration = live_client.post(
        "/api/auth/register",
        json={"email": "rate@example.com", "password": "secure-test-password"},
    )
    token = registration.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    first = live_client.post("/api/ai/ask", headers=headers, json={"question": "Explain React"})
    limited = live_client.post("/api/ai/ask", headers=headers, json={"question": "Explain state"})

    assert first.status_code == 200
    assert limited.status_code == 429
    assert limited.json()["detail"] == "Too many AI requests. Please wait a minute and try again."


def test_daily_ai_limit_returns_friendly_429(live_client, monkeypatch) -> None:
    import app.api.routes.ai as ai_route

    settings = Settings(
        database_url="sqlite://",
        jwt_secret="test-only-signing-key-with-at-least-32-characters",
        ai_daily_limit_per_user=1,
        ai_rate_limit_per_minute=10,
    )
    monkeypatch.setattr(ai_route, "get_settings", lambda: settings)
    registration = live_client.post(
        "/api/auth/register",
        json={"email": "daily@example.com", "password": "secure-test-password"},
    )
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}

    first = live_client.post("/api/ai/ask", headers=headers, json={"question": "Explain React"})
    limited = live_client.post("/api/ai/ask", headers=headers, json={"question": "Explain state"})

    assert first.status_code == 200
    assert limited.status_code == 429
    assert limited.json()["detail"] == "Daily AI limit reached, try again tomorrow"


def test_demo_login_isolated_from_regular_users(live_client, monkeypatch) -> None:
    import app.api.routes.auth as auth_route
    import app.api.routes.ai as ai_route

    settings = Settings(
        database_url="sqlite://",
        jwt_secret="test-only-signing-key-with-at-least-32-characters",
        demo_mode=True,
        demo_password="a-test-demo-password",
        ai_daily_limit_per_user=4,
        demo_ai_daily_limit_per_user=1,
        ai_rate_limit_per_minute=10,
    )
    monkeypatch.setattr(auth_route, "get_settings", lambda: settings)
    monkeypatch.setattr(ai_route, "get_settings", lambda: settings)
    factory = live_client.app.state.test_session_factory
    with factory() as db:
        seed_demo_data(db, settings)

    regular = live_client.post(
        "/api/auth/register",
        json={"email": "regular@example.com", "password": "secure-test-password"},
    )
    regular_headers = {
        "Authorization": f"Bearer {regular.json()['access_token']}"
    }
    created = live_client.post(
        "/api/notes",
        headers=regular_headers,
        json={"title": "Private", "description": "Only for this account"},
    )
    assert created.status_code == 201

    demo = live_client.post("/api/auth/demo-login")
    assert demo.status_code == 200
    assert demo.json()["user_id"] == DEMO_USER_ID
    demo_headers = {"Authorization": f"Bearer {demo.json()['access_token']}"}
    demo_notes = live_client.get("/api/notes", headers=demo_headers)

    assert len(demo_notes.json()) == 3
    assert all(note["title"] != "Private" for note in demo_notes.json())
    assert live_client.delete(
        f"/api/notes/{created.json()['id']}",
        headers=demo_headers,
    ).status_code == 404
    assert live_client.post(
        "/api/ai/ask",
        headers=demo_headers,
        json={"question": "Explain photosynthesis"},
    ).status_code == 200
    limited = live_client.post(
        "/api/ai/ask",
        headers=demo_headers,
        json={"question": "Explain React state"},
    )
    assert limited.status_code == 429
    assert limited.json()["detail"] == "Daily AI limit reached, try again tomorrow"


def test_ai_generation_failure_does_not_expose_exception(live_client, monkeypatch) -> None:
    import app.api.routes.ai as ai_route

    def fail_generation(*args, **kwargs):
        raise RuntimeError("provider secret must not appear in the response")

    monkeypatch.setattr(ai_route, "generate_ai_answer", fail_generation)
    registration = live_client.post(
        "/api/auth/register",
        json={"email": "failure@example.com", "password": "secure-test-password"},
    )
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}

    response = live_client.post(
        "/api/ai/ask",
        headers=headers,
        json={"question": "Explain React"},
    )

    assert response.status_code == 502
    assert response.json() == {
        "detail": "AI service is temporarily unavailable. Please try again."
    }


def test_ai_timeout_returns_safe_504(live_client, monkeypatch) -> None:
    import time
    import app.api.routes.ai as ai_route

    settings = Settings(
        database_url="sqlite://",
        jwt_secret="test-only-signing-key-with-at-least-32-characters",
        ai_request_timeout_seconds=0.01,
    )
    monkeypatch.setattr(ai_route, "get_settings", lambda: settings)

    def slow_generation(*args, **kwargs):
        time.sleep(0.05)
        return {"answer": "late", "topic_detected": "default", "sources": []}

    monkeypatch.setattr(ai_route, "generate_ai_answer", slow_generation)
    registration = live_client.post(
        "/api/auth/register",
        json={"email": "timeout@example.com", "password": "secure-test-password"},
    )
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}

    response = live_client.post(
        "/api/ai/ask",
        headers=headers,
        json={"question": "Explain React"},
    )

    assert response.status_code == 504
    assert response.json() == {"detail": "AI request timed out. Please try again."}


def test_demo_seed_refuses_to_claim_an_existing_account(live_client) -> None:
    settings = Settings(
        database_url="sqlite://",
        jwt_secret="test-only-signing-key-with-at-least-32-characters",
        demo_mode=True,
        demo_password="a-test-demo-password",
    )
    factory = live_client.app.state.test_session_factory
    with factory() as db:
        db.add(
            User(
                id="00000000-0000-4000-8000-000000000099",
                email=settings.demo_email,
                hashed_password="unrelated",
            )
        )
        db.commit()
        try:
            seed_demo_data(db, settings)
        except RuntimeError as error:
            assert "non-demo account" in str(error)
        else:
            raise AssertionError("Demo seeding must not take over a regular account.")
