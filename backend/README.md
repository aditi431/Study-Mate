# StudyMate backend

FastAPI backend for account authentication, private study notes, and the local
StudyMate AI prototype.

## Implemented

- Email/password registration and login
- HS256 JWT access tokens
- Authenticated note create, list, search, update, and delete
- Per-user note isolation
- Persistent AI chat sessions and messages
- Local knowledge-bank AI responses
- SQLite for local development and PostgreSQL for production
- Alembic database migrations
- Health check endpoint

## Local setup

```powershell
Copy-Item .env.example .env
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs`.

## Production setup

Set these environment variables:

- `ENVIRONMENT=production`
- `JWT_SECRET=<at least 32 random characters>`
- `JWT_ALGORITHM=HS256`
- `JWT_EXPIRE_MINUTES=10080`
- `DATABASE_URL=<PostgreSQL connection URL>`
- `CORS_ORIGINS=<exact deployed frontend origin>`

The production configuration rejects SQLite and default JWT secrets.

The Docker command runs `alembic upgrade head` before starting Uvicorn.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Public health check |
| `POST` | `/api/auth/register` | Create an account |
| `POST` | `/api/auth/login` | Create an access token |
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
