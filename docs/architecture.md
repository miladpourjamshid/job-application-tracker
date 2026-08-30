# Architecture

```text
HTTP / FastAPI routes
        |
        v
Application Service
        |
        v
Application Repository
        |
        v
SQLAlchemy Session
        |
        v
SQLite / PostgreSQL
```

Routes handle HTTP concerns and validation. Services contain business rules. Repositories encapsulate database access. Alembic owns schema migrations.
