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

Two tariffs: `standard` and `pro`. Subscription statuses: `process → active → not_active`. On activation, balance is debited and a `HistoryPayment` record is created. A Celery beat task (`checking_subscription_relevance`) runs every second to expire subscriptions past their `expiration_date`.

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
