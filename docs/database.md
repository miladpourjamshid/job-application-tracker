# Database

## Local development

The default database is SQLite for zero-configuration local development.

```bash
alembic upgrade head
```

To create a new migration after changing SQLAlchemy models:

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```

The migration history is committed to the repository so another developer can
reproduce the schema from scratch with `alembic upgrade head`.

## PostgreSQL

Set `DATABASE_URL` to a PostgreSQL SQLAlchemy URL, e.g.
`postgresql+psycopg://user:password@host:5432/job_tracker`. The Psycopg
driver is already a project dependency. The application reads the database
URL from environment configuration, so the same application code runs
unmodified against SQLite or PostgreSQL.

## Design

- HTTP concerns live in the route layer (`main.py`).
- Business rules live in the service layer (`services.py`).
- Persistence and query logic live in the repository layer (`repositories.py`).
- Schema changes are versioned with Alembic instead of relying on
  `create_all()` for production deployments.
- Indexes cover the columns used for filtering and sorting: company, status,
  applied date, deadline, and the foreign keys tying applications to users,
  companies, contacts, and interviews.
