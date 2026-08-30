# Job Application Tracker

> A production-minded REST API for tracking job applications, built with Python, FastAPI, SQLAlchemy, Alembic, SQLite/PostgreSQL, pytest, and GitHub Actions.

## Final release

**v1.0.0 — Final portfolio release**

This release contains the completed backend scope for the portfolio project. It provides authenticated, user-scoped job application tracking with companies, contacts, interviews, history, pagination, filtering, and dashboard reporting.

### Included

- User accounts with unique email addresses
- Argon2 password hashing through `pwdlib`
- JWT access tokens and OAuth2 password flow
- Authenticated user-owned application data
- Cross-user data isolation
- Companies, contacts, interviews, and application history
- Pagination and filtering
- User-scoped dashboard statistics
- Upcoming interview and deadline counts
- Status, offer, and rejection summaries
- Alembic migration lifecycle tests
- Ruff linting
- GitHub Actions on Python 3.12 and 3.13
- SQLite and PostgreSQL support

## API

### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Dashboard

- `GET /dashboard`

The dashboard is authenticated and scoped to the current user's applications.

### Applications

- `POST /applications`
- `GET /applications`
- `GET /applications/{application_id}`
- `PATCH /applications/{application_id}`
- `DELETE /applications/{application_id}`
- `GET /applications/{application_id}/history`
- `POST /applications/{application_id}/interviews`
- `GET /applications/{application_id}/interviews`

### Companies and contacts

- `POST /companies`
- `GET /companies`
- `GET /companies/{company_id}`
- `POST /companies/{company_id}/contacts`
- `GET /companies/{company_id}/contacts`

## Architecture

```text
job-application-tracker/
├── .github/workflows/ci.yml
├── alembic/versions/
├── docs/
├── src/job_tracker/
│   ├── auth.py
│   ├── config.py
│   ├── db.py
│   ├── main.py
│   ├── models.py
│   ├── pagination.py
│   ├── repositories.py
│   ├── schemas.py
│   ├── services.py
│   └── version.py
├── tests/
├── .env.example
├── .gitignore
├── alembic.ini
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
└── README.md
```

## Tech stack

- Python 3.12+
- FastAPI
- SQLAlchemy 2
- Alembic
- SQLite
- PostgreSQL / psycopg
- Pydantic Settings
- PyJWT
- pwdlib + Argon2
- Pytest + coverage
- Ruff
- GitHub Actions

## Run locally

```bash
git clone https://github.com/miladpourjamshid/job-application-tracker.git
cd job-application-tracker

python -m venv .venv
source .venv/bin/activate
# Windows: .venv\\Scripts\\activate

pip install -e ".[dev]"
alembic upgrade head
uvicorn job_tracker.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for the interactive API documentation.

## Quality checks

```bash
ruff check .
pytest --cov=job_tracker --cov-report=term-missing --cov-fail-under=80
```

Validate the migration lifecycle:

```bash
alembic upgrade head
alembic downgrade base
alembic upgrade head
```

## Engineering goals

1. Clear separation of concerns
2. Strong input validation
3. Testable application boundaries
4. Versioned and reproducible database changes
5. Secure credential handling
6. Reproducible development setup
7. CI checks on every change

## License

MIT
