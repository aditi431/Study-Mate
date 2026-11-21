from fastapi.testclient import TestClient

def test_health_is_available_without_configuration(client: TestClient) -> None:
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
