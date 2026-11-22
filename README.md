# StudyMate

StudyMate is a full-stack study workspace for private notes and a local, knowledge-bank-based study assistant.

## What is implemented

- Email/password sign-up and login with signed JWTs.
- Authenticated note creation, editing, deletion, and search.
- Per-user note and chat-session ownership in the SQLAlchemy data layer.
- Configurable MySQL and PostgreSQL database URLs (MySQL is the recommended deployment target).
- A local AI prototype with simple, example, and quiz response modes.
- Per-IP per-minute and per-user daily AI limits.
- Optional recruiter demo login with isolated sample data.
- Health endpoint at `/api/health`.

The active React application is [`studymate-react/`](./studymate-react/), which is the app built by Render. [`frontend/`](./frontend/) is an older static prototype and is not deployed by the current Render blueprint.

## Backend setup

Use Python 3.11 or newer and a MySQL server. The database URL should use the `mysql+pymysql` driver:

```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

The backend reads configuration from `backend/.env` (and process environment variables override it). Keep the existing `.env` file; it is private and is not committed. Set a unique `JWT_SECRET` (at least 32 characters) and a valid `DATABASE_URL`. For example:

```text
DATABASE_URL=mysql+pymysql://studymate_user:your-password@localhost:3306/studymate
```

Create the `studymate` database and its application user in MySQL before starting the API. For local testing without MySQL, `DATABASE_URL=sqlite:///./studymate.db` is also supported. The application creates missing tables on startup; Alembic migrations can be run with `alembic upgrade head`.

Run the API from `backend/`:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API and interactive docs are at `http://127.0.0.1:8000` and `http://127.0.0.1:8000/docs`.

## Frontend setup

```powershell
cd ..\studymate-react
Copy-Item .env.example .env
npm ci
npm run dev
```

Set `VITE_API_URL` to the backend base URL, including `/api` (local default: `http://127.0.0.1:8000/api`). The Docker deployment reads `VITE_API_URL` when the container starts.

## Environment variables

| Variable | Required | Purpose |
|---|---:|---|
| `DATABASE_URL` | Yes | SQLAlchemy URL. MySQL (`mysql+pymysql://...`) recommended; PostgreSQL and SQLite are supported. |
| `JWT_SECRET` | Yes | Unique signing secret, at least 32 characters. Do not reuse the example value. |
| `JWT_ALGORITHM` | No | JWT signing algorithm; defaults to `HS256`. |
| `JWT_EXPIRE_MINUTES` | No | Token lifetime; defaults to 10080 (7 days). |
| `APP_NAME` | No | API title; defaults to `StudyMate API`. |
| `ENVIRONMENT` | No | Use `production` to reject SQLite. |
| `ALLOWED_ORIGINS` | No | Comma-separated exact browser origins. `CORS_ORIGINS` remains a compatible alias. |
| `FORWARDED_ALLOW_IPS` | No | Trusted proxy addresses for Uvicorn's client IP handling; Render is configured to trust its ingress proxy. |
| `GEMINI_API_KEY` | No | Reserved for a future Gemini integration; the current AI prototype does not use it. |
| `AI_DAILY_LIMIT_PER_USER` | No | Daily AI requests for regular users; defaults to 20. |
| `AI_RATE_LIMIT_PER_MINUTE` | No | AI requests per client IP in a rolling minute; defaults to 10. |
| `AI_REQUEST_TIMEOUT_SECONDS` | No | AI response timeout; defaults to 10 seconds. |
| `DEMO_MODE` | No | Enables demo account seeding and the login endpoint; defaults to `false`. |
| `DEMO_EMAIL` | No | Demo account email; defaults to `demo@studymate.local`. |
| `DEMO_PASSWORD` | When demo is on | Demo password, at least 12 characters. Supply privately; no default password is shipped. |
| `DEMO_AI_DAILY_LIMIT_PER_USER` | No | Demo account daily AI cap; defaults to 3 and must be lower than the regular cap. |
| `VITE_API_URL` | No | Frontend API base URL, including `/api`. |

The app loads `backend/.env`, not `.env.example`; process environment variables take precedence. It fails at startup if `DATABASE_URL` or `JWT_SECRET` is missing. Placeholder values for `JWT_SECRET` and demo passwords are rejected. `GEMINI_API_KEY` is optional because no external LLM is currently called. Never commit `.env` or paste its secrets into the Render blueprint; enter production values in Render's private environment settings.

## Demo account

Set `DEMO_MODE=true` and provide `DEMO_PASSWORD` to enable the **Try Demo** button. The demo email defaults to `demo@studymate.local`; its password is the value configured by the operator in `DEMO_PASSWORD` (for Render, set it as a private environment variable). No real user password or notes are copied into the demo account. Demo notes and chat history are scoped to a dedicated demo user ID, and all note operations remain user-scoped.

Seeded demo notes are added on startup. To reset only the demo account's notes and chat history, run from `backend/`:

```powershell
python reset_demo.py
```

## AI behavior and limits

The current assistant returns answers from a bundled knowledge bank and appends a note-context hint. **It does not call Gemini or another LLM**, and it is not retrieval-augmented question answering over full note contents. Requests are limited to 2,000 characters, with configurable per-IP/minute and per-user/day limits. A `429` response displays a readable message in the chat. The in-memory limit tracker is per application process: restarts reset counters, and multiple replicas do not share counters. Use a shared limiter store before scaling across processes or replicas.

## Tests

The backend tests use FastAPI `TestClient` and isolated SQLite databases:

```powershell
cd backend
python -m pytest
```

The tests cover authentication, note CRUD and ownership, AI limits, and demo-login isolation. No MySQL server is configured in this workspace, so live MySQL connectivity still needs verification against the deployment database.

## Render deployment

The root `render.yaml` defines a native Python FastAPI service and the `studymate-react` Docker frontend. Environment variables are intentionally not declared in either YAML file: configure them in each Render service's **Environment** settings. The backend uses:

- **Root directory:** `backend`
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check:** `/api/health`

Before deploying:

1. In the backend Render service's Environment settings, set `ENVIRONMENT=production`, `DATABASE_URL`, `JWT_SECRET` (unique, at least 32 characters), `ALLOWED_ORIGINS`, and `FORWARDED_ALLOW_IPS=*`. To enable demo login, also set `DEMO_MODE=true` and a private `DEMO_PASSWORD` (at least 12 characters). The regular and demo AI limits default to 20 and 3.
2. In the frontend Render service's Environment settings, set `VITE_API_URL=https://studymate-api.onrender.com/api`.
3. Ensure backend `ALLOWED_ORIGINS` contains the exact deployed frontend origin (`https://studymate-web.onrender.com`, or the custom domain).
4. Deploy the backend and frontend. The backend start command runs Alembic before Uvicorn; the frontend container writes its runtime API URL from `VITE_API_URL`.

The existing Render PostgreSQL resource is retained in the blueprint to avoid removing or destroying an existing resource, but the backend expects `DATABASE_URL` to be set in the Render dashboard. It is not automatically connected; enter the PostgreSQL connection string or connect a MySQL-compatible database.

## Planned work

- [ ] PDF uploads and text extraction.
- [ ] Full-note retrieval-augmented question answering and external LLM integration.
- [ ] Generated summaries, quizzes, flashcards, and personalized revision plans.

---

Built by Aditi Sharma while learning full-stack application development.
