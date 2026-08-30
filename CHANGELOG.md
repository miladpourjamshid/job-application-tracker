# Changelog

## 1.0.0 — Final portfolio release

- User accounts with unique email addresses.
- Argon2 password hashing through `pwdlib`.
- JWT access tokens and OAuth2 password flow.
- Authenticated, user-owned application data with cross-user isolation.
- Legacy-data migration path so pre-auth records get a safe owner on upgrade.

## 0.3.0 — Domain expansion

- Companies, contacts, interviews, and application history.
- Cross-entity validation (contacts must belong to a real company, interviews
  must reference a real application/contact, etc.).

## 0.2.0 — Database engineering

- Alembic-based schema versioning.
- Repository and service layers separating persistence from business rules.
- Database query indexes for common filters.
- Typed pagination primitives.
- SQLite for development, PostgreSQL for deployment.

## 0.1.0 — Initial release

- Core `JobApplication` model and CRUD endpoints.
- Status, applied date, and deadline tracking.
