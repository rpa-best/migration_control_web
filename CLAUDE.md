# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Миграскоп** — Django REST API backend for migration control: managing foreign workers, their documents, organizations, subscriptions, and automatically generating legal documents.

## Commands

**Run locally (Docker):**
```bash
docker-compose up --build
```
Server starts on port `5002`. Requires `.env` file (see env vars below).

**Apply migrations:**
```bash
docker exec dev_migration_control_web python manage.py migrate
```

**Create superuser:**
```bash
docker exec dev_migration_control_web python manage.py createsuperuser
```

**Run Celery worker manually (without Docker):**
```bash
celery -A migration_control_web worker --pool solo
celery -A migration_control_web beat
```

**Syntax check after editing Python files:**
```bash
python3 -m py_compile <file.py>
```

## Required `.env` Variables

```
SECRET_KEY=
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=
POSTGRES_PORT=
EMAIL_HOST_USER=
EMAIL_HOST_PASSWORD=
PORT=5002
CORS_ALLOWED_ORIGINS=
ALLOWED_HOSTS=
CLIENT_SIGNING_KEY=
DEBUG=
```

## Production Infrastructure

### Servers

| Role | Host | Details |
|------|------|---------|
| Backend + Frontend | `88.218.168.214` | root SSH access |
| Database (PostgreSQL) | `45.8.96.179` | external managed DB |

### Server 88.218.168.214 — layout

| Container | Port | Path |
|-----------|------|------|
| `migration_control_web` (Django/Gunicorn) | 8000 | `/var/www/migration-control-web/` |
| `migrascope-front` (Next.js) | 4000 | `/var/www/migrascope-new/` |
| `migration_control_celery` | — | same image as backend |
| `migration_control_celery_beat` | — | same image as backend |
| `migration_control_redis` | 6379 | Alpine Redis |

Nginx proxies:
- `https://api.migradocs.ru` → `localhost:8000`
- `https://migradocs.ru` → `localhost:4000`

Backend compose: `/var/www/migration-control-web/docker-compose.yml`
Backend env: `/var/www/migration-control-web/.env`
Frontend env: `/var/www/migrascope-new/.env.local`

### Database 45.8.96.179

- DB name: `migration_control_db`
- User: `gen_user`
- Port: `5432`
- **Important:** there is at least one other database on this server — do not touch it.

### Deploy commands (backend)

```bash
# Upload changed files via SCP, then:
cd /var/www/migration-control-web && docker compose up -d --force-recreate migration_control_web
# Use --force-recreate (not restart) to pick up .env changes
```

### Deploy commands (frontend)

```bash
cd /var/www/migrascope-new && npm run build && docker compose up -d --force-recreate
```

### Run one-off Django scripts on server

```bash
docker cp script.py migration_control_web:/app/script.py
docker exec migration_control_web python /app/script.py
docker exec migration_control_web rm /app/script.py
```

## Architecture

All business logic lives in the single Django app `v1_1/`. The project module `migration_control_web/` contains only settings, URL root, and Celery config.

### URL structure

Base prefix: `api/v1.1/`

| Path | Module |
|------|--------|
| `account/` | user registration, auth, profile, balance |
| `organization/` | organizations, banks, directors, MIA addresses |
| `worker/` | foreign workers, their documents |
| `blanks/` | document generation (Word/PDF templates) |
| `tasks/` | periodic compliance tasks per worker |
| `news/` | news feed |

### Swagger docs

Split into 6 separate schemas, each at `api/v1.1/schema-<domain>/`. Main Swagger UI at `api/v1.1/docs/`. Hooks that filter endpoints per schema are in `v1_1/swagger_content/hooks.py`.

### Authentication

JWT via `simplejwt`. Header: `Authorization: Bearer <token>`. `USERNAME_FIELD` is set to `username` but the `username` column stores **email**, not a login string — auth is email-based. Token lifetimes: access 1 day, refresh 30 days.

### Permission system (`v1_1/permissions/`)

| Class | Condition |
|-------|-----------|
| `IsOwner` | User authenticated + has active `Subscription` |
| `IsnOwnerInOrganization` | User is `owner` role in given org + active subscription |
| `IsAdmin` | User is `admin` or `owner` role in org |
| `IsObserver` | Any role in org (observer, admin, owner) |

Most write endpoints require `IsOwner`. Access is gated by subscription status before checking org roles.

### Subscription model (`v1_1/models/subscription.py`)

Three tariffs: `basic` (free, 1 org / 5 workers), `standard` (1990₽, 3 orgs / 50 workers), `pro` (4990₽, 10 orgs / 500 workers). Subscription statuses: `process → active → not_active`. On activation, balance is debited and a `HistoryPayment` record is created. A Celery beat task (`checking_subscription_relevance`) runs every 60s to expire subscriptions past their `expiration_date`. Any active subscription (including `basic`) is sufficient for document management; only `pro` gates the Blanks section.

### Worker lifecycle (`v1_1/models/worker.py`)

Statuses: `vacancy → accepted → dismissed`. On dismissal, all pending `Tasks` for the worker's documents are deleted. Worker has `DocumentsWorker` (passport, migration card, patent, etc.) and `FileDocuments` (actual file uploads).

### Document generation (`v1_1/common_utils/generation_*.py`)

Uses `docxtpl` to render `.docx` templates stored in `templates/`. One generator per document type: employment contract, arrival notice, notice of conclusion/termination, payment order, suspension order, contract for paid services.

### Celery tasks

All three beat tasks run every second (defined in `settings.py` `CELERY_BEAT_SCHEDULE`):
- `checking_subscription_relevance` — expires overdue subscriptions
- `payment_for_worker` — periodic worker salary payments
- `task_formation` — auto-generates compliance tasks for workers

Broker and result backend: Redis at `migration_control_redis:6379`.

### Custom utilities

- `v1_1/common_utils/paginations.py` — `CustomPagination` (default for all endpoints)
- `v1_1/common_utils/swagger_schema.py` — `CustomAutoSchema` auto-appends 400/401/403 responses to every endpoint
- `v1_1/apies/DaData.py` — DaData API integration for organization lookup by INN
- `v1_1/common_utils/pvc.py` — PVC (phone verification code) generation and SMS/email sending
