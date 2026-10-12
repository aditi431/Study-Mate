# StudyMate backend

The backend is a FastAPI service for account-protected StudyMate notes. It uses
Supabase Auth to identify users and PostgreSQL for persistent data. The React
app sends a Supabase access token to the API; the API verifies that token, then
filters every note operation by the verified account ID. It never accepts a
user ID from note input.

## What is implemented

- `GET /api/health` works without a database or Supabase configuration.
- Supabase access-token verification supports the project's JWKS signing keys
  (ES256/RS256/EdDSA). Legacy HS256 projects can use `SUPABASE_JWT_SECRET`.
- Authenticated note create, list, update, delete, and title/description search.
- Alembic schema migration for profiles, notes, documents, document chunks, and
  pgvector embeddings. PostgreSQL row-level security (RLS) and a Supabase Auth
  trigger keep rows associated with the owning account.
- The React Notes view signs up/signs in against Supabase Auth and uses the API
  for persistent notes.
- Pytest API tests run against a temporary SQLite database.

The document tables are groundwork only: document upload/ingestion, chunking,
embedding generation, retrieval, and real AI answers are **not implemented**.
`POST /api/ai/ask` returns HTTP 501 rather than inventing answers.

## Requirements

- Python 3.12 (3.11+ should also work)
- A Supabase project for account authentication and PostgreSQL storage
- Node.js/npm for the React application

## Configure and run

From PowerShell in the `backend` directory:

```powershell
Copy-Item .env.example .env
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Edit `.env` and provide:

- `SUPABASE_URL`: the project URL from Supabase **Settings → API**.
- `DATABASE_URL`: a PostgreSQL connection URI. Use a direct or session-pooler
  connection, and require TLS (`sslmode=require`). Use the database password
  from Supabase **Settings → Database**. Never commit `.env`.
- `CORS_ORIGINS`: comma-separated frontend origins, normally
  `http://localhost:5173` for local development.
- `SUPABASE_JWT_SECRET`: only for older projects whose access-token JWT
  algorithm is HS256. Projects using asymmetric signing keys should leave it
  blank; the API obtains their public key from the project's JWKS endpoint.

Run the database migration and API:

```powershell
alembic upgrade head
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for the OpenAPI page. The health endpoint is
`http://127.0.0.1:8000/api/health`. The migration requires a database role
allowed to create the schema objects, enable RLS, create the Auth trigger, and
set the `authenticated` role. Supabase's project database owner connection
normally has those privileges.

In Supabase **Authentication → Providers → Email**, enable email/password
authentication. Email confirmation can be enabled; new users then need to
confirm their email before signing in. The migration creates a matching profile
when Supabase inserts or updates an Auth user.

## Configure and run the React app

From `studymate-react`:

```powershell
Copy-Item .env.example .env
npm install
```

Set `VITE_SUPABASE_URL` and `VITE_SUPABASE_ANON_KEY` to the Supabase project URL
and its public anon/publishable key. Set `VITE_API_URL` if the API is not at
`http://127.0.0.1:8000/api`. The anon key is intended for browser use; **never**
put a Supabase service-role key or database password in a `VITE_` variable.

Start Vite with `npm run dev`. Access tokens are kept in `sessionStorage` and
sent only as bearer tokens to the API. Sign out clears the stored token. Use
HTTPS in production and set exact production origins in backend `CORS_ORIGINS`.

## API

All note endpoints require `Authorization: Bearer <Supabase access token>`.

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | Health check; no credentials required |
| `GET` | `/api/notes` | List the signed-in user's notes |
| `GET` | `/api/notes/search?q=...` | Search the signed-in user's note titles and descriptions |
| `POST` | `/api/notes` | Create a note (`title`, `description`, optional `topics_count`) |
| `PATCH` | `/api/notes/{id}` | Update supplied note fields |
| `DELETE` | `/api/notes/{id}` | Delete a note |
| `POST` | `/api/ai/ask` | Explicitly returns 501 until retrieval and a model are configured |

Note IDs are UUIDs. `topics_count` is a non-negative integer. Note list and
search results are ordered newest first. A note owned by another account is
reported as not found on update/delete, so the API does not reveal its
existence.

## Tests

From `backend` after installing requirements:

```powershell
python -m pytest
```

The tests exercise API validation, authentication gates, CRUD, search, and
cross-account isolation using SQLite and dependency overrides. They do not
replace a deployment check against Supabase PostgreSQL; RLS and Auth triggers
must also be verified in a configured Supabase project before production use.

## Current AI/RAG boundary

AI API credentials have configuration placeholders, and document/chunk/vector
tables are migrated, but no provider client, document endpoint, ingestion
pipeline, similarity search, prompt construction, or answer generation is
implemented. Configure those as a separate feature before enabling the
`/api/ai/ask` route. The current endpoint reports this as unavailable instead
of returning fabricated answers.
