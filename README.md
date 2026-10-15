# Law Case Management

Starter project for a legal case intake and assignment system.

## Workflow

1. A client submits a case form with a title, category, and case description without needing an account.
2. An administrator creates lawyer accounts and assigns submitted cases to lawyers.
3. Lawyers can view only cases assigned to them.

Public self-registration is intentionally absent. The first administrator is created with Django's `createsuperuser` command; subsequent lawyer accounts are managed in Django admin.

## Stack

- Django REST Framework API, PostgreSQL database `law`
- React + Vite client
- pytest / pytest-django
- Docker Compose and Jenkins pipeline

## Run with Docker

1. Copy `.env.example` to `.env` and replace the PostgreSQL user/password and Django secret key placeholders with local values. Never commit `.env`; it is excluded by `.gitignore`.
2. Run `docker compose up --build` (PostgreSQL is the only supported database).
3. In another terminal, create the initial administrator: `docker compose exec api python manage.py createsuperuser`.
4. Open the React client at http://localhost:5174 and the Django admin at http://localhost:8000/admin/.

The initial API endpoints are documented below. Lawyers and administrators use session login in the React portal. Every new account created through Django admin is automatically marked as staff and assigned to the `Lawyer` group, so no manual role selection is needed. Create the initial administrator separately with `createsuperuser`. In production, configure HTTPS, secure cookies, allowed hosts, and a dedicated identity/token strategy.

## API

- `POST /api/cases/` — anonymous clients can submit a case without creating an account.
- `GET /api/cases/` — administrators see all cases; lawyers see only assigned cases; anonymous clients do not list cases.
- `GET/PATCH /api/cases/{id}/` — retrieve own/assigned case; administrators may update status and assignment.
- `GET /api/lawyers/` — administrator-only list of lawyer accounts for assignment.

Roles are Django groups: `Lawyer` and `Administrator` (Django staff/superuser). Create groups in Django admin and add users to the appropriate group. Only lawyer accounts are created and managed by administrators; public clients are not registered in the system.

## Local development

Backend: use PostgreSQL and set `POSTGRES_HOST`, `POSTGRES_DB`, `POSTGRES_USER`, and `POSTGRES_PASSWORD`, install `backend/requirements.txt`, then run migrations and `python manage.py runserver` in `backend/`.

Frontend: use Node.js 20 or later, then run `cd frontend && npm install && npm run dev`. Vite is pinned to the 5.x line to support Node.js 20.9.

Tests are located under `backend/cases/tests/`; run with `pytest` from `backend/`.
