# Orisync

A production-grade supply chain event tracking API with webhook delivery,
role-based access control, observability, and CI/CD.

**Live API:** https://orisync-production.up.railway.app  
**API Docs:** https://orisync-production.up.railway.app/docs  
**Health:** https://orisync-production.up.railway.app/health

![CI](https://github.com/iamwizzyg/orisync/actions/workflows/ci.yml/badge.svg)

---

## The Problem

Small manufacturers and logistics teams track supplier deliveries, inventory
movements, and purchase orders manually or through spreadsheets. When a
shipment is delayed or an anomaly occurs, they find out late. Orisync provides
a backend system that ingests supply chain events, stores them with full audit
history, fires webhook notifications to external systems on state changes, and
exposes a clean REST API for querying.

---

## What I Built

A REST API that:

- Accepts supply chain events (ORDERED, SHIPPED, DELAYED, RECEIVED, ANOMALY)
  from any internal or external system
- Stores events permanently with idempotency protection against duplicate
  submissions
- Fires webhook notifications to registered endpoints when events match
  subscription rules
- Retries failed webhook deliveries with exponential backoff
- Signs webhook payloads with HMAC-SHA256 so receivers can verify authenticity
- Enforces role-based access control across three roles: ADMIN, OPERATOR, VIEWER
- Exposes Prometheus metrics for API throughput, event volumes, and webhook
  delivery rates
- Deploys to cloud with automated database migrations on every release

---

## Architecture
┌─────────────────────────────────────────────────────┐
│                   CLIENT / CALLER                    │
│         (Postman, external system, test suite)       │
└──────────────────────┬──────────────────────────────┘
│ HTTPS
▼
┌─────────────────────────────────────────────────────┐
│              FastAPI Application                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │   Auth   │  │  Routes  │  │   Prometheus      │  │
│  │  JWT     │  │  + RBAC  │  │   /metrics        │  │
│  └──────────┘  └──────────┘  └──────────────────┘  │
│                      │                               │
│         ┌────────────▼──────────────┐               │
│         │   Background Task Worker  │               │
│         │   Webhook Dispatcher      │               │
│         │   HMAC signing + retries  │               │
│         └────────────┬──────────────┘               │
└──────────────────────┼──────────────────────────────┘
│
┌─────────────┼──────────────┐
▼             ▼              ▼
┌────────────┐  ┌─────────┐  ┌────────────┐
│ PostgreSQL │  │ External│  │ Prometheus │
│  Railway   │  │  hooks  │  │  metrics   │
└────────────┘  └─────────┘  └────────────┘

GitHub Actions CI/CD:
push → lint (ruff) → test (pytest, 85% coverage) → Docker build → deploy

---

## Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Framework | FastAPI | Type-safe, auto-documented, async-capable |
| Database | PostgreSQL | Production standard, JSONB support |
| ORM | SQLAlchemy 2.0 | Industry standard Python ORM |
| Migrations | Alembic | Versioned schema changes |
| Auth | JWT + bcrypt | Stateless authentication, secure password storage |
| Webhook signing | HMAC-SHA256 | Payload verification standard (same as Stripe) |
| Observability | Prometheus | Time-series metrics, industry standard |
| Containerisation | Docker | Consistent environments across dev and prod |
| CI/CD | GitHub Actions | Automated lint, test, and build on every push |
| Deployment | Railway | Cloud deployment with managed PostgreSQL |

---

## API Reference

Full interactive documentation: https://orisync-production.up.railway.app/docs

### Authentication

All endpoints except `/health` and `/metrics` require a Bearer token.

```bash
# Register
POST /api/v1/auth/register
{"email": "user@example.com", "password": "securepass", "role": "OPERATOR"}

# Login — returns access token
POST /api/v1/auth/login
{"email": "user@example.com", "password": "securepass"}
Core Endpoints
POST   /api/v1/suppliers              Create supplier
GET    /api/v1/suppliers              List active suppliers
POST   /api/v1/events                 Ingest supply event (triggers webhooks)
GET    /api/v1/events                 Query events with filters
POST   /api/v1/subscriptions          Register webhook endpoint
GET    /api/v1/deliveries             View webhook delivery logs
POST   /api/v1/deliveries/{id}/retry  Manually retry failed delivery
GET    /health                        Health check
GET    /metrics                       Prometheus metrics

Roles

Role	Can do
ADMIN	Everything
OPERATOR	Create events and suppliers, read all
VIEWER	Read only

Key Engineering Decisions

Idempotency on event ingestion. Each event accepts an optional
idempotency_key. If the same key is submitted twice (network retry, duplicate
request), the API returns the original event instead of creating a duplicate.
This is standard practice in distributed systems.

Webhook delivery with HMAC signing. When Orisync delivers a webhook, it
signs the payload with HMAC-SHA256 using the subscription's secret key. The
receiving system can verify the X-Orisync-Signature header to confirm the
request is genuine. This is the same approach used by Stripe and GitHub.

Background task dispatch. Webhook delivery happens in a FastAPI background
task so the event ingestion endpoint responds immediately without waiting for
HTTP calls to external systems. Each delivery attempt is logged separately with
its response code and body.

Exponential backoff on retry. Failed deliveries retry at 60s, 120s, and
240s intervals. After three failures, the delivery is marked permanently failed
and can be manually retried via the API.

Layered architecture. Routes handle HTTP only. Services contain business
logic. Models handle persistence. This separation makes each layer independently
testable and mirrors the structure used in production engineering teams.

Running Locally

Requirements

	•	Python 3.11
	•	Docker and Docker Compose

Setup
git clone https://github.com/iamwizzyg/orisync.git
cd orisync

python3.11 -m venv .venv
source .venv/bin/activate

pip install -e ".[dev]"

cp .env.example .env
# Edit .env and set SECRET_KEY to a random 32+ character string

docker compose up -d

alembic upgrade head

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
Visit http://localhost:8000/docs

Running Tests
# Create test database first
docker exec -it orisync_db psql -U orisync_user -d postgres \
  -c "CREATE DATABASE orisync_test;"

pytest tests/ -v --cov=app --cov-report=term-missing
Test results: 44 tests, 85% coverage
Every push to main runs:

	1.	Ruff linting
	2.	Full test suite with coverage gate (75% minimum)
	3.	Docker image build

Deployment to Railway happens automatically after a successful pipeline.

Security

	•	Passwords hashed with bcrypt (minimum 8 characters enforced)
	•	JWT tokens expire after 30 minutes
	•	Webhook payloads signed with HMAC-SHA256
	•	Role-based access control on every protected endpoint
	•	Environment variables for all secrets (never hardcoded)
	•	Non-root user inside Docker container
	•	Input validation via Pydantic on all request bodies

Project Structure
app/
├── api/v1/endpoints/   # Route handlers (HTTP layer only)
├── core/               # Security (JWT) and metrics (Prometheus)
├── db/                 # Database connection and session management
├── models/             # SQLAlchemy table definitions
├── schemas/            # Pydantic request/response models
└── services/           # Business logic (auth, events, webhooks)



Idempotency is harder than it looks. A unique constraint on idempotency_key
handles the database-level guarantee, but the application also needs to return
the existing resource rather than a 409 error, which requires checking before
inserting.

Background tasks in FastAPI are simple to add but introduce a separate
execution context. The webhook dispatcher needs its own database session
because the request session closes before the background task runs.

CI caught real bugs. The GitHub Actions environment exposed a SQLAlchemy mapper
initialization race condition in background threads that never appeared locally.
Running tests in CI is not optional.

---

Now open `docs/architecture.md` and paste this:

```markdown
# Orisync Architecture

## System Overview

Orisync is a REST API built with FastAPI, PostgreSQL, and deployed on Railway.
It follows a layered architecture with clear separation between HTTP handling,
business logic, and data persistence.

## Request Flow


HTTP Request
↓
Route Handler (app/api/v1/endpoints/)
— validates auth token via dependency injection
— parses and validates request body via Pydantic schema
↓
Service Layer (app/services/)
— executes business logic
— enforces domain rules (idempotency, supplier validation)
↓
SQLAlchemy Model (app/models/)
— maps Python objects to PostgreSQL tables
↓
PostgreSQL Database
↓
Pydantic Response Schema
— serializes DB model to JSON
— strips sensitive fields (hashed_password never returned)
↓
HTTP Response

## Data Model

Five tables with the following relationships:


users               (authentication and RBAC)

suppliers           (registered supply chain partners)
└── supply_events (events associated with a supplier)
└── webhook_deliveries (delivery attempts per event)

subscriptions       (webhook endpoints registered to receive events)
└── webhook_deliveries (delivery attempts per subscription)

## Webhook Delivery Flow

POST /api/v1/events
↓
Event stored in supply_events (status: PENDING)
↓
Background task dispatched (non-blocking)
↓
Active subscriptions queried
↓
For each matching subscription:
— payload serialized to JSON
— payload signed with HMAC-SHA256 if secret_key set
— HTTP POST sent to webhook_url
— delivery attempt logged in webhook_deliveries
↓
If delivery fails:
— status set to FAILED
— next_retry_at calculated with exponential backoff
— retry scheduled
↓
Event status updated to PROCESSED

## Security Model

Authentication: JWT tokens (HS256, 30-minute expiry)
Authorization: Role-based (ADMIN > OPERATOR > VIEWER)
Password storage: bcrypt with minimum 8-character enforcement
Webhook verification: HMAC-SHA256 signature in X-Orisync-Signature header
Secrets: Environment variables only, never committed to version control
Container: Non-root user (appuser)

## Technology Choices

FastAPI over Flask: automatic OpenAPI documentation, native async,
Pydantic integration, type safety at the HTTP boundary.

PostgreSQL over SQLite: production-grade, JSONB for flexible event payloads,
proper concurrent access, available as managed service on Railway.

SQLAlchemy 2.0 over raw SQL: type-safe queries, relationship loading,
connection pooling, database-agnostic migration via Alembic.

Prometheus over custom logging for metrics: pull-based scraping,
industry-standard format, integrates directly with Grafana.



