# Random Letter Generator

A small asynchronous FastAPI service that generates random uppercase letters and stores them in PostgreSQL.

## Requirements

- Python 3.13.5
- PostgreSQL 17.2

Set `DATABASE_URL` to a PostgreSQL connection string. If it is not set, the service uses:

```text
postgresql://postgres:postgres@localhost:5432/postgres
```

Copy `.env.example` as a reference for the required setting.

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application creates the `letters` table automatically at startup.

## API

- `POST /letters/generate` — create and persist one random `A`–`Z` letter (`201 Created`)
- `GET /letters` — list all generated letters, newest first
- `GET /letters/{letter_id}` — retrieve one letter (`404` with `{"detail":"Letter not found"}` when missing)
