# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Insurance Core (incore)** is a monorepo containing a full-stack insurance management system:
- **Backend**: FastAPI + Python 3.12 (async) on port 8000
- **Frontend**: Next.js 15 + TypeScript + React 18 on port 3000
- **Database**: PostgreSQL 16 (async-first with SQLAlchemy 2.0 + asyncpg)
- **Development**: Docker Compose for local development

**Architecture**: Domain-Driven Design (DDD) with separate domains for policyholders, policies, etc.

### 🔴 Code Quality Requirement

**All Python code MUST strictly follow PEP 8 standard** ([PEP 8 Guide](https://pep8.org/))

This is enforced via Ruff linting (configured in `pyproject.toml`). Any Python code that violates PEP 8 will be rejected. Before committing, run:
```bash
ruff check backend/
```

---

## Essential Commands

### Backend Setup & Running

```bash
# Install dependencies (from /backend)
uv pip install -e .           # Install package in dev mode
uv pip install -e ".[dev]"    # Install with dev dependencies

# Run server (from /backend)
uvicorn app.main:app --reload

# Database migrations (from /backend)
alembic upgrade head          # Apply all pending migrations
alembic revision --autogenerate -m "description"  # Create new migration

# Testing
pytest tests/ -v              # Run all tests
pytest tests/test_file.py -v  # Run specific test file
./run_tests.sh               # Run via script (installs dev deps first)
```

### Frontend Setup & Running

```bash
# Install dependencies (from /frontend)
yarn install

# Development server
yarn dev                      # Runs on http://localhost:3000

# Testing
yarn test                     # Run Vitest tests
yarn test:ui                  # Run tests with UI
yarn test:coverage            # Run with coverage

# Linting
yarn lint                     # Run ESLint

# Build for production
yarn build
yarn start
```

### Docker

```bash
# From root directory
docker-compose up             # Start all services (postgres, backend, frontend)
docker-compose up -d          # Start in background
docker-compose down           # Stop services
docker-compose logs -f        # View logs
```

### Local Development

```bash
# Start both services (run in separate terminals from root):
docker-compose up

# OR start individually:
cd backend && uvicorn app.main:app --reload     # Port 8000
cd frontend && yarn dev                          # Port 3000

# API docs: http://localhost:8000/docs (Swagger)
# API ReDoc: http://localhost:8000/redoc
# Frontend: http://localhost:3000
```

---

## Backend Architecture

### Directory Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI app entry point + exception handlers
│   ├── core/
│   │   ├── config.py          # Settings (pydantic-settings)
│   │   ├── database.py        # Async engine, sessionmaker, Base class
│   │   ├── security.py        # JWT utilities, password hashing
│   │   ├── exceptions.py      # Custom exception classes
│   │   ├── logging.py         # Structured logging (structlog) ✅
│   │   ├── middleware.py      # Request/response logging middleware ✅
│   │   └── dependencies.py    # Ownership validation helpers ✅
│   ├── domains/                # Business domains (DDD)
│   │   ├── policy_holders/    # Policyholders domain (Phase 2) ✅
│   │   ├── policies/          # Policies domain (Phase 3) ✅
│   │   ├── underwriting/      # Underwriting (Phase 5) ✅
│   │   ├── pricing/           # Pricing/Quotes (Phase 4) ✅
│   │   ├── billing/           # Billing/Payments (Phase 6) ✅
│   │   └── users/             # Auth (Phase 7) ✅
│   ├── workflows/             # Cross-domain workflows (Phase 8) ✅
│   │   ├── quote_to_policy.py # Quote-to-Policy workflow
│   │   ├── schemas.py         # Workflow schemas
│   │   └── router.py          # Workflow endpoints
│   └── shared/
│       ├── schemas/base.py    # Base Pydantic schemas, pagination
│       ├── enums.py           # Insurance domain enums (Phase 1) ✅
│       └── types.py           # Type aliases
├── alembic/                    # Database migrations
├── tests/                      # Test suite (pytest + pytest-asyncio)
└── pyproject.toml             # Dependencies, tool config
```

### Domain Structure

Each domain follows this pattern (see `policy_holders/` and `policies/` as examples):

```
domains/{domain}/
├── __init__.py
├── models.py          # SQLAlchemy ORM models
├── schemas.py         # Pydantic request/response schemas
├── repository.py      # Data access layer (CRUD with async)
├── service.py         # Business logic
├── router.py          # FastAPI routes (includes prefix from main.py)
└── exceptions.py      # Domain-specific exceptions (optional)
```

### Key Technical Decisions

- **Async-First**: All database operations are async (asyncpg driver)
- **ORM**: SQLAlchemy 2.0 (not tightly coupled, flexible)
- **Naming**: PEP 8 (modules/tables: `policy_holders`, classes: `PolicyHolder`)
- **Migrations**: Alembic (auto-generate from models: `alembic revision --autogenerate`)
- **Auth**: JWT with role-based access control (ADMIN, UNDERWRITER, AGENT, CUSTOMER)
- **Logging**: Structured logging with structlog (JSON/readable formats)
- **Validation**: Pydantic v2 (with custom validators in schemas)

### Testing Strategy

- **Test Location**: `tests/` directory mirrors `app/` structure
- **Framework**: pytest + pytest-asyncio (asyncio_mode="auto" in pyproject.toml)
- **Coverage Target**: >80% per module
- **Async Tests**: Use `async def test_...()` for async operations
- **Database**: Use fixtures for test DB isolation

---

## Frontend Architecture

### Key Files & Directories

- `src/app/` - Next.js 14 App Router (pages, layouts, components)
- `next.config.js` - Next.js configuration
- `tailwind.config.js` - TailwindCSS config (if using)
- `vitest.config.ts` - Vitest configuration

### Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Testing**: Vitest
- **Linting**: ESLint with next/eslint-plugin

### API Integration

- Backend API base URL: `process.env.NEXT_PUBLIC_API_URL` (default: http://localhost:8000)
- API docs available at: http://localhost:8000/docs

---

## Database & Migrations

### Schema

Current tables (see Phase 2-3 implementations):
- `policy_holders` - Customer/policyholder records (Phase 2 ✅)
- `policies` - Insurance policies (Phase 3 ✅)
- `coverages` - Policy coverages (Phase 3 ✅)

**PostgreSQL table naming**: Use plural form with snake_case for compound words (e.g., `policy_holders`, `underwriting_reviews`)

### Creating Migrations

```bash
cd backend

# Auto-generate from model changes
alembic revision --autogenerate -m "add status field to policies"

# Review the generated migration
# Apply it
alembic upgrade head
```

### Running Tests Against Real DB

Tests use real PostgreSQL (via docker-compose). Make sure postgres service is running:

```bash
# In separate terminal
docker-compose up postgres

# Then run tests
cd backend && pytest tests/ -v
```

---

## Development Workflow

### Before Making Changes

1. **Create a feature branch**: `git checkout -b feature/phase-X-description`
2. **Check the IMPLEMENTATION_PLAN.md**: See what's planned for your phase
3. **Run existing tests**: `pytest tests/ -v` (backend) or `yarn test` (frontend)
4. **Verify docker-compose works**: `docker-compose up` (should start cleanly)

### When Adding a New Domain

1. Create directory: `backend/app/domains/{domain_name}/`
2. Add files: `__init__.py`, `models.py`, `schemas.py`, `repository.py`, `service.py`, `router.py`
3. Create migration: `alembic revision --autogenerate -m "add {domain} tables"`
4. Import router in `app/main.py`: `app.include_router(router, prefix=settings.API_V1_STR)`
5. Write tests in `tests/{domain}/`
6. Update IMPLEMENTATION_PLAN.md

### Code Style

**All Python code MUST follow PEP 8 standard** ([PEP 8 Guide](https://pep8.org/))

- **Backend**: Ruff (E, F, I checks at line-length 88) enforces PEP 8 compliance
  - Run: `ruff check backend/` to verify compliance
  - Naming: PEP 8 required
    - Modules/packages: `lowercase_with_underscores`
    - Classes: `PascalCase`
    - Functions/variables: `lowercase_with_underscores`
    - Constants: `UPPERCASE_WITH_UNDERSCORES`
  - Line length: 88 characters max
  - Indentation: 4 spaces (no tabs)
  - Two blank lines between top-level definitions, one between methods
- **Frontend**: ESLint (next config)
  - Run: `yarn lint`

### Commit Messages

Follow conventional commits:
- `feat:` new feature
- `fix:` bug fix
- `refactor:` code restructuring
- `docs:` documentation
- `test:` test additions/changes
- `chore:` tooling, dependencies

Example: `feat: add policy renewal endpoint` or `fix: enforce PEP 8 naming conventions`

---

## Important Files & Configurations

### Backend Config Files

- `pyproject.toml` - Dependencies, ruff config, pytest config
- `alembic.ini` - Alembic migration configuration
- `docker-compose.yml` - Full stack setup with postgres, backend, frontend
- `.env.example` - Example environment variables (copy to `.env`)

### Frontend Config Files

- `package.json` - Scripts, dependencies
- `tsconfig.json` - TypeScript configuration
- `vitest.config.ts` - Test configuration

### Environment Variables

**Backend** (`.env` or docker-compose):
- `DATABASE_URL` - PostgreSQL connection (must use `postgresql+asyncpg://`)
- `JWT_SECRET_KEY` - Secret for JWT signing
- `JWT_ALGORITHM` - HS256 (recommended)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - 30 (default)

**Frontend** (`.env.local` or docker-compose):
- `NEXT_PUBLIC_API_URL` - Backend API URL (must start with `NEXT_PUBLIC_`)

---

## Common Development Tasks

### Run Backend Tests Only

```bash
cd backend
pytest tests/ -v
# Or specific test
pytest tests/test_policy_holders.py::test_create_policy_holder -v
```

### Debug Async Tests

```bash
# Add breakpoint in test
import pdb; pdb.set_trace()

# Run pytest with -s flag to see output
pytest tests/ -v -s
```

### Check Database State

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U insurance_user -d insurance_core

# List tables
\dt

# Query policyholders
SELECT * FROM policy_holders;
```

### Reset Database (in docker)

```bash
docker-compose down -v    # Remove volume
docker-compose up         # Recreates DB
alembic upgrade head      # Apply all migrations
```

### Clear Cache & Dependencies

```bash
# Backend
cd backend && rm -rf .ruff_cache backend.egg-info

# Frontend
cd frontend && rm -rf node_modules .next yarn.lock && yarn install
```

---

## Implementation Phases Status

Current Progress: **Phase 8/9 (89%)**

| Phase | Name | Status | Notes |
|-------|------|--------|-------|
| 0 | Foundation & Infrastructure | ✅ Complete | Async DB, JWT, exceptions, alembic |
| 1 | Shared Domain Models & Enums | ✅ Complete | PolicyStatus, Gender, RiskLevel, etc. |
| 2 | Policyholders Domain | ✅ Complete | CRUD endpoints, PEP 8 naming enforced |
| 3 | Policies Domain | ✅ Complete | Policy + Coverage models, auto-generation |
| 4 | Pricing/Quoting Domain | ✅ Complete | Quote model, PricingEngine service |
| 5 | Underwriting Domain | ✅ Complete | Risk scoring, UnderwritingReview |
| 6 | Billing/Payments Domain | ✅ Complete | Stripe integration, Invoice/Payment models |
| 7 | Authentication & Authorization | ✅ Complete | User model, JWT login, RBAC |
| 8 | Integration & Polish | ✅ Complete | Logging, workflows, health checks, indexes |

See `docs/IMPLEMENTATION_PLAN.md` for detailed phase specifications.

---

## Debugging Tips

### Backend: View SQL Queries

Add to FastAPI app (for development only):
```python
import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
```

### Backend: Test a Single Endpoint

```bash
# From backend directory
python -c "
import asyncio
from app.domains.policy_holders.service import PolicyHolderService
from app.core.database import get_db

# Use test fixtures or real DB
"
```

### Frontend: React DevTools

- Install React DevTools browser extension
- Use `yarn test:ui` to run tests visually

---

## References

- **FastAPI Docs**: https://fastapi.tiangolo.com/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **Pydantic v2**: https://docs.pydantic.dev/
- **Alembic**: https://alembic.sqlalchemy.org/
- **Next.js**: https://nextjs.org/docs
- **pytest**: https://docs.pytest.org/

---

**Last Updated**: 2026-04-02  
**Project**: Insurance Core (incore)  
**Status**: Active Development (Phase 3/9)
