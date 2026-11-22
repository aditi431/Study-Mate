# StudyMate backend

FastAPI service for authentication, per-user study notes, and the local StudyMate AI prototype.

## Implemented

- Email/password sign-up and login with bcrypt password hashes and HS256 JWTs.
- Authenticated note create, list, search, update, and delete, all scoped to the signed-in user.
- SQLAlchemy persistence with MySQL, PostgreSQL, or SQLite database URLs.
- Optional seeded demo account with isolated sample notes and a targeted reset script.
- Per-IP/minute and per-user/day AI request limits and a request timeout.
- Local knowledge-bank responses (no external LLM call).
- Alembic migrations and `/api/health`.

## Local setup

```powershell
Copy-Item .env.example .env
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

Set `DATABASE_URL` and a unique `JWT_SECRET` (at least 32 characters) in `.env`. The example config uses MySQL; SQLite is also supported for local testing. Then start the API:

```powershell
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

When `DEMO_MODE=true`, configure `DEMO_PASSWORD` (at least 12 characters). The demo user and sample notes are seeded during application startup. Run `python reset_demo.py` from this directory to reset only the demo notes and chat history.

## Production setup

Required: `DATABASE_URL` and a unique `JWT_SECRET`. Set `ENVIRONMENT=production`, `ALLOWED_ORIGINS` to the exact frontend origin, and any enabled demo credentials as private environment variables. Production rejects SQLite. `GEMINI_API_KEY` is optional and currently unused.

AI limits default to 10 requests per IP per minute, 20 per user per day, and 3 per demo user per day. The in-memory tracker is process-local; use shared storage before deploying multiple workers or replicas.

For a native Python deployment on Render, set the root directory to `backend`, the build command to `pip install -r requirements.txt`, and the start command to `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`. Set the health check path to `/api/health`.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Public health check |
| `POST` | `/api/auth/register` | Create an account |
| `POST` | `/api/auth/login` | Create an access token |
| `POST` | `/api/auth/demo-login` | Sign in to the seeded demo account when enabled |
| `GET` | `/api/auth/me` | Get the signed-in account |
| `GET` | `/api/notes` | List signed-in user's notes |
| `GET` | `/api/notes/search?q=...` | Search signed-in user's notes |
| `POST` | `/api/notes` | Create a note |
| `PATCH` | `/api/notes/{id}` | Update a note |
| `DELETE` | `/api/notes/{id}` | Delete a note |
| `POST` | `/api/ai/ask` | Ask the local AI prototype |
| `GET` | `/api/ai/sessions` | List chat sessions |
| `GET` | `/api/ai/sessions/{id}` | Get session messages |
| `DELETE` | `/api/ai/sessions/{id}` | Delete a session |

## Tests

```powershell
python -m pytest
```
