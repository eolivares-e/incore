# Insurance Core - Implementation Plan

## 📊 Current Status
- **Current Phase**: Phase 7 - Authentication & Authorization (🟢 COMPLETE)
- **Progress**: 7/9 Phases Complete (78%)
- **Last Updated**: 2026-04-03
- **Status**: 🟢 Phase 7 Complete, Ready for PR #9

---

## 🎯 Phases Overview

| Phase | Name | Status | PR Link | Completion |
|-------|------|--------|---------|------------|
| 0 | Foundation & Infrastructure | 🟢 Complete | [PR #1](https://github.com/eolivares-e/incore/pull/1) | 100% |
| 1 | Shared Domain Models & Enums | 🟢 Complete | [PR #3](https://github.com/eolivares-e/incore/pull/3) | 100% |
| 2 | Policyholders Domain | 🟢 Complete | [PR #4](https://github.com/eolivares-e/incore/pull/4) | 100% |
| 3 | Policies Domain | 🟢 Complete | [PR #5](https://github.com/eolivares-e/incore/pull/5) | 100% |
| 4 | Pricing/Quoting Domain | 🟢 Complete | [PR #6](https://github.com/eolivares-e/incore/pull/6) | 100% |
| 5 | Underwriting Domain | 🟢 Complete | [PR #7](https://github.com/eolivares-e/incore/pull/7) | 100% |
| 6 | Billing/Payments Domain | 🟢 Complete | [PR #8](https://github.com/eolivares-e/incore/pull/8) | 100% |
| 7 | Authentication & Authorization | 🟢 Complete | - | 100% |
| 8 | Integration & Polish | ⚪ Not Started | - | 0% |

**Legend**: 🟢 Complete | 🟡 In Progress | ⚪ Not Started | 🔴 Blocked

---

## 🏗️ Architecture Overview

### Technology Stack
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0 (async)
- **Migrations**: Alembic
- **Validation**: Pydantic v2
- **Authentication**: JWT
- **Payment Gateway**: Stripe
- **Testing**: pytest + pytest-asyncio
- **Package Manager**: uv

### Architecture Pattern
**Domain-Driven Design (DDD)**

```
backend/
├── app/
│   ├── main.py                      # FastAPI app entry point
│   ├── core/                        # Core configuration & shared utilities
│   │   ├── config.py               # Settings & environment
│   │   ├── database.py             # DB connection & session
│   │   ├── security.py             # JWT & auth utilities
│   │   └── exceptions.py           # Custom exceptions
│   ├── domains/                     # Business domains
│   │   ├── policyholders/          # Policyholder domain
│   │   ├── policies/               # Policy domain
│   │   ├── underwriting/           # Underwriting domain
│   │   ├── pricing/                # Pricing/Quoting domain
│   │   ├── billing/                # Billing/Payments domain
│   │   └── users/                  # Users & Auth domain
│   └── shared/                      # Shared across domains
│       ├── schemas/                # Common Pydantic schemas
│       ├── enums.py                # Common enums
│       └── types.py                # Common types
├── alembic/                         # DB migrations
├── tests/                           # Test suite
└── docs/                            # Documentation
```

### Domain Structure Template
Each domain follows this structure:
```
domains/{domain_name}/
├── __init__.py
├── models.py           # SQLAlchemy models (DB layer)
├── schemas.py          # Pydantic schemas (API layer)
├── repository.py       # Data access layer
├── service.py          # Business logic
├── router.py           # FastAPI routes
└── exceptions.py       # Domain-specific exceptions
```

---

## 📋 Detailed Phase Plans

---

## Phase 0: Foundation & Infrastructure 🔧

**Objective**: Setup basic infrastructure and dependencies

**Status**: 🟢 Complete  
**Branch**: `feature/phase-0-foundation`  
**PR**: [#1](https://github.com/eolivares-e/incore/pull/1) ✅ **MERGED**  
**Started**: 2026-04-02  
**Completed**: 2026-04-02

### Tasks Checklist
- [x] Task 1: Update pyproject.toml with dependencies
- [x] Task 2: Configure PostgreSQL in docker-compose.yml
- [x] Task 3: Setup core/database.py (async engine, session)
- [x] Task 4: Setup core/config.py (settings management)
- [x] Task 5: Setup core/security.py (JWT utilities)
- [x] Task 6: Initialize Alembic (migrations setup)
- [x] Task 7: Setup core/exceptions.py (custom exceptions)
- [x] Write tests for core modules
- [x] Update documentation
- [x] Create PR

### Task Details

#### Task 1: Update pyproject.toml
Add dependencies:
- `sqlalchemy[asyncio]>=2.0.0` - Async ORM
- `asyncpg>=0.29.0` - PostgreSQL async driver
- `alembic>=1.13.0` - Database migrations
- `python-jose[cryptography]>=3.3.0` - JWT tokens
- `passlib[bcrypt]>=1.7.4` - Password hashing
- `python-multipart>=0.0.9` - Form data support

#### Task 2: Configure PostgreSQL
- Add postgres service to docker-compose.yml
- Configure environment variables
- Setup volumes for data persistence
- Add health checks

#### Task 3: Setup core/database.py
- Create async engine with asyncpg
- Configure async sessionmaker
- Create Base declarative class
- Implement get_db() dependency for FastAPI
- Add database initialization function

#### Task 4: Setup core/config.py
- Extend Settings class with:
  - Database URL (with async driver)
  - JWT settings (secret key, algorithm, expiration)
  - CORS configuration
  - Environment-specific settings
- Use pydantic-settings for validation

#### Task 5: Setup core/security.py
- JWT token creation function
- JWT token validation function
- Password hashing utilities
- Password verification
- OAuth2PasswordBearer scheme
- get_current_user dependency (placeholder)

#### Task 6: Initialize Alembic
- Run `alembic init alembic`
- Configure alembic.ini for async
- Update env.py for async operations
- Configure target_metadata from Base
- Create initial migration template

#### Task 7: Setup core/exceptions.py
- Define base custom exceptions:
  - `InsuranceCoreException` (base)
  - `NotFoundException`
  - `ValidationException`
  - `AuthenticationException`
  - `AuthorizationException`
- Register exception handlers in main.py

### Deliverables
- ✅ All infrastructure dependencies installed
- ✅ PostgreSQL configured and running
- ✅ Database connection working (async)
- ✅ Alembic migrations initialized
- ✅ JWT utilities ready
- ✅ Custom exceptions framework
- ✅ Tests passing
- ✅ Documentation updated

### Testing Strategy
- Test database connection
- Test settings loading from environment
- Test JWT token creation/validation
- Test password hashing/verification
- Integration test with docker-compose

---

## Phase 1: Shared Domain Models & Enums 📦

**Objective**: Define common types and enumerations for the insurance domain

**Status**: 🟡 In Progress (Complete, Creating PR)  
**Branch**: `feature/phase-1-shared-domain`  
**PR**: PR #2 (Creating)  
**Dependencies**: Phase 0  
**Started**: 2026-04-02  
**Completed**: 2026-04-02

### Tasks Checklist
- [x] Create shared/enums.py with insurance domain enums
- [x] Create shared/types.py with common type aliases
- [x] Create shared/schemas/base.py with base schemas
- [x] Write tests for enums and schemas
- [x] Update documentation

### Enums to Implement
- `PolicyStatus` (DRAFT, ACTIVE, EXPIRED, CANCELLED, SUSPENDED, PENDING_RENEWAL)
- `PolicyType` (AUTO, HOME, LIFE, HEALTH)
- `ClaimStatus` (SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, PAID, CLOSED)
- `PaymentStatus` (PENDING, COMPLETED, FAILED, REFUNDED, CANCELLED)
- `PaymentMethod` (CREDIT_CARD, DEBIT_CARD, BANK_TRANSFER, CASH, CHECK)
- `UnderwritingStatus` (PENDING, APPROVED, REJECTED, REQUIRES_REVIEW)
- `CoverageType` (LIABILITY, COLLISION, COMPREHENSIVE, MEDICAL, PROPERTY_DAMAGE)
- `Gender` (MALE, FEMALE, OTHER, PREFER_NOT_TO_SAY)
- `RiskLevel` (LOW, MEDIUM, HIGH, VERY_HIGH)
- `IdentificationType` (PASSPORT, DRIVER_LICENSE, NATIONAL_ID, SSN)

### Base Schemas
- `BaseSchema` - Common Pydantic config
- `TimestampMixin` - created_at, updated_at fields
- `PaginationParams` - page, size, ordering
- `PaginatedResponse[T]` - Generic paginated response

---

## Phase 2: Policyholders Domain 👥

**Objective**: CRUD for insurance policyholders/customers

**Status**: 🟡 In Progress (Complete, Creating PR)  
**Branch**: `feature/phase-2-policyholders`  
**PR**: PR #4 (Creating)  
**Dependencies**: Phase 0, Phase 1  
**Started**: 2026-04-02  
**Completed**: 2026-04-02

### Tasks Checklist
- [x] Create models.py (Policyholder SQLAlchemy model)
- [x] Create schemas.py (Pydantic schemas)
- [x] Create repository.py (data access layer)
- [x] Create service.py (business logic)
- [x] Create router.py (FastAPI endpoints)
- [x] Create Alembic migration
- [x] Write unit tests
- [x] Update documentation

### Policyholder Model Fields
- id (UUID primary key)
- first_name, last_name
- email (unique, indexed)
- phone
- date_of_birth
- gender (enum)
- address (street, city, state, zip_code, country)
- identification_type (enum)
- identification_number
- is_active (boolean)
- created_at, updated_at (timestamps)

### API Endpoints
- `POST /api/v1/policyholders` - Create policyholder
- `GET /api/v1/policyholders/{id}` - Get by ID
- `GET /api/v1/policyholders` - List (paginated, filterable)
- `PUT /api/v1/policyholders/{id}` - Update
- `DELETE /api/v1/policyholders/{id}` - Soft delete

### Business Rules
- Email must be unique
- Age must be between 18-100 years
- Phone number validation
- Address validation

---

## Phase 3: Policies Domain (Core) 📄

**Objective**: Core policy management functionality

**Status**: 🟢 Complete  
**Branch**: `feature/phase-3-policies`  
**PR**: [#5](https://github.com/eolivares-e/incore/pull/5) (Ready for Merge)  
**Dependencies**: Phase 2  
**Started**: 2026-04-02  
**Completed**: 2026-04-02

### Tasks Checklist
- [x] Create Policy and Coverage models
- [x] Create schemas for Policy and Coverage
- [x] Create PolicyRepository and CoverageRepository
- [x] Create PolicyService with business logic
- [x] Create router with endpoints
- [x] Implement policy_number auto-generation
- [x] Create Alembic migrations
- [x] Write tests
- [x] Update documentation

### Policy Model Fields
- id (UUID)
- policy_number (unique, auto-generated)
- policyholder_id (FK to policyholders)
- policy_type (enum)
- status (enum)
- effective_date, expiration_date
- premium_amount (Decimal)
- coverage_amount (Decimal)
- deductible (Decimal)
- terms_and_conditions (Text/JSON)
- created_at, updated_at

### Coverage Model Fields
- id (UUID)
- policy_id (FK to policies)
- coverage_type (enum)
- coverage_amount (Decimal)
- description (Text)

### API Endpoints
- `POST /api/v1/policies` - Create policy
- `GET /api/v1/policies/{id}` - Get policy (with coverages)
- `GET /api/v1/policies` - List policies (filters, pagination)
- `PUT /api/v1/policies/{id}` - Update policy
- `POST /api/v1/policies/{id}/renew` - Renew policy
- `POST /api/v1/policies/{id}/cancel` - Cancel policy
- `GET /api/v1/policies/by-number/{policy_number}` - Get by policy number

### Business Rules
- Policy number format: `POL-{YEAR}-{TYPE}-{SEQUENCE}`
- effective_date must be < expiration_date
- Cannot cancel already cancelled policy
- Renewal creates new policy with new dates
- Premium and coverage amounts must be > 0

---

## Phase 4: Pricing/Quoting Domain 💰

**Objective**: Quote generation and premium calculation

**Status**: ⚪ Not Started  
**Branch**: `feature/phase-4-pricing`  
**PR**: -  
**Dependencies**: Phase 3

### Tasks Checklist
- [ ] Create Quote and PricingRule models
- [ ] Create schemas
- [ ] Create repositories
- [ ] Create PricingEngine service
- [ ] Create QuoteService
- [ ] Create router
- [ ] Implement risk assessment logic
- [ ] Create migrations
- [ ] Write tests
- [ ] Update documentation

### Quote Model Fields
- id (UUID)
- quote_number (unique, auto-generated)
- policyholder_id (FK)
- policy_type (enum)
- requested_coverage_amount (Decimal)
- calculated_premium (Decimal)
- risk_factors (JSON) - factors used in calculation
- risk_level (enum)
- valid_until (DateTime)
- status (PENDING, ACCEPTED, REJECTED, EXPIRED)
- created_at

### PricingRule Model Fields
- id (UUID)
- policy_type (enum)
- risk_level (enum)
- base_premium (Decimal)
- multiplier_factors (JSON)
- is_active (boolean)

### API Endpoints
- `POST /api/v1/quotes` - Request quote
- `GET /api/v1/quotes/{id}` - Get quote
- `GET /api/v1/quotes` - List quotes
- `POST /api/v1/quotes/{id}/accept` - Accept quote (creates policy)
- `GET /api/v1/pricing-rules` - List pricing rules (admin)
- `POST /api/v1/pricing-rules` - Create rule (admin)

### Pricing Logic
- Base premium from PricingRule
- Risk factors: age, policy_type, coverage_amount, etc.
- Apply multipliers based on risk assessment
- Calculate final premium
- Store calculation details in risk_factors JSON

---

## Phase 5: Underwriting Domain ✅

**Objective**: Risk assessment and policy approval

**Status**: 🟢 Complete  
**Branch**: `feature/phase-5-underwriting`  
**PR**: [#7](https://github.com/eolivares-e/incore/pull/7) ✅ **OPEN**  
**Started**: 2026-04-02  
**Completed**: 2026-04-02  
**Dependencies**: Phase 4

### Tasks Checklist
- [x] Create UnderwritingReview model
- [x] Create schemas (8 total: Create, Update, Approve, Reject, Response, List, FilterParams)
- [x] Create repository with advanced filtering
- [x] Create UnderwritingService with RiskScoringEngine
- [x] Create router (8 endpoints)
- [x] Implement auto-approval rules (risk_score < 30 = AUTO-APPROVE)
- [x] Create migrations (migration 004)
- [x] Write tests (22 comprehensive tests, all passing)
- [x] Update documentation
- [x] Add relationships to Quote and Policy models

### Implementation Summary

**Models** (`domains/underwriting/models.py`):
- UnderwritingReview with 15 fields
- Properties: is_pending, is_decided, is_auto_approved
- Check constraints: risk_score range (0-100), quote/policy exclusivity

**Business Logic** (`domains/underwriting/service.py`):
- RiskScoringEngine: Dual calculation methods (quote-based, policy-based)
- UnderwritingService: Auto-approval workflow, manual operations
- Auto-approve if risk_score < 30
- Manual review required if risk_score >= 70
- Medium risk (30-69) defaults to IN_REVIEW

**API Endpoints** (8 total):
- POST /reviews - Create review (auto-calculates risk)
- GET /reviews/{id} - Get by ID
- GET /reviews - List with filters
- GET /reviews/pending/all - Pending queue for dashboard
- PUT /reviews/{id} - Update
- POST /reviews/{id}/approve - Manual approval
- POST /reviews/{id}/reject - Manual rejection (notes required)

**Testing**:
- 22 new tests (models, schemas, risk scoring, service)
- All 145 tests passing (123 existing + 22 new)

**Files Created**: 8 files, 2136 lines
- Complete underwriting domain (6 files)
- Migration 004
- Comprehensive test suite

### UnderwritingReview Model Fields
- id (UUID)
- policy_id or quote_id (FK)
- reviewer_id (FK to users - nullable for auto)
- status (enum: PENDING, APPROVED, REJECTED)
- risk_assessment (JSON) - detailed risk factors
- risk_level (enum)
- risk_score (Integer 0-100)
- notes (Text)
- approved_at, rejected_at (nullable timestamps)
- created_at, updated_at

### API Endpoints
- `POST /api/v1/underwriting/reviews` - Submit for review
- `GET /api/v1/underwriting/reviews/{id}` - Get review
- `GET /api/v1/underwriting/reviews` - List reviews (pending)
- `POST /api/v1/underwriting/reviews/{id}/approve` - Approve
- `POST /api/v1/underwriting/reviews/{id}/reject` - Reject

### Business Rules
- Auto-approve if risk_score < 30 (LOW risk)
- Manual review required if risk_score >= 70 (HIGH/VERY_HIGH)
- Risk factors: age, policy amount, history, etc.

---

## Phase 6: Billing/Payments Domain 💳

**Objective**: Invoice management and Stripe payment integration

**Status**: ⚪ Not Started  
**Branch**: `feature/phase-6-billing`  
**PR**: -  
**Dependencies**: Phase 3

### Tasks Checklist
- [ ] Create Invoice and Payment models
- [ ] Create schemas
- [ ] Create repositories
- [ ] Create PaymentProvider interface (abstract)
- [ ] Create StripeProvider implementation
- [ ] Create BillingService and PaymentService
- [ ] Create router (including webhook endpoint)
- [ ] Add Stripe SDK dependency
- [ ] Configure Stripe settings in config.py
- [ ] Create migrations
- [ ] Write tests (with Stripe mocked)
- [ ] Update documentation

### Invoice Model Fields
- id (UUID)
- invoice_number (unique, auto-generated)
- policy_id (FK)
- amount_due (Decimal)
- due_date (Date)
- paid_date (Date, nullable)
- status (PENDING, PAID, OVERDUE, CANCELLED)
- created_at, updated_at

### Payment Model Fields
- id (UUID)
- invoice_id (FK)
- amount (Decimal)
- payment_method (enum)
- payment_date (DateTime)
- transaction_id (String) - external reference
- stripe_payment_intent_id (String, nullable)
- status (enum: PENDING, COMPLETED, FAILED, REFUNDED)
- metadata (JSON) - payment gateway data
- created_at

### API Endpoints
- `POST /api/v1/invoices` - Generate invoice
- `GET /api/v1/invoices/{id}` - Get invoice
- `GET /api/v1/invoices` - List invoices
- `POST /api/v1/payments/create-intent` - Create Stripe payment intent
- `POST /api/v1/payments` - Record payment
- `GET /api/v1/payments/{id}` - Get payment
- `POST /api/v1/payments/{id}/refund` - Refund payment
- `POST /api/v1/webhooks/stripe` - Stripe webhook receiver

### Stripe Integration
- Payment intent creation
- Payment confirmation via webhook
- Refund processing
- Webhook signature verification
- Environment variables for API keys

**Note**: User will configure Stripe credentials

---

## Phase 7: Authentication & Authorization 🔐

**Objective**: JWT-based authentication and role-based access control

**Status**: 🟢 Complete  
**Branch**: `feature/phase-7-auth`  
**PR**: - (Ready for creation)  
**Dependencies**: Phase 0  
**Started**: 2026-04-03  
**Completed**: 2026-04-03

### Tasks Checklist
- [x] Create User model (with UserRole enum)
- [x] Create schemas (UserCreate, UserResponse, UserRegister, UserLogin, TokenResponse, TokenRefresh)
- [x] Create UserRepository (CRUD + auth methods)
- [x] Create AuthService (register, login, token management, authorization)
- [x] Create auth_router (register, login, refresh, logout, me endpoints)
- [x] Create users_router (admin-only user management: list, get, update, activate, deactivate)
- [x] Implement JWT token refresh (access + refresh tokens, no rotation)
- [x] Create CLI command for admin user creation
- [x] Implement role-based authorization (validate_user_for_action method)
- [x] Create migration (users table with 9 columns, 3 indexes, 2 check constraints)
- [x] Write comprehensive tests (30 tests: model, schema, repository, service)
- [x] Update documentation (CLAUDE.md, planning docs)
- [x] Verify all tests pass (181 tests passing)

### User Model Fields
- id (UUID, primary key)
- email (unique, indexed)
- hashed_password (String)
- full_name (String)
- role (enum: ADMIN, UNDERWRITER, AGENT, CUSTOMER)
- is_active (Boolean, default True)
- is_superuser (Boolean, default False)
- created_at, updated_at (timestamps)

### API Endpoints

#### Auth Endpoints (`/api/v1/auth`)
- `POST /auth/register` - Register new user (defaults to CUSTOMER role)
- `POST /auth/login` - Login (returns access + refresh tokens)
- `POST /auth/refresh` - Refresh access token using refresh token
- `POST /auth/logout` - Logout (placeholder - client-side token deletion)
- `GET /auth/me` - Get current authenticated user info

#### User Management Endpoints (`/api/v1/users`) - Admin Only
- `GET /users` - List all users (paginated, with role filter)
- `GET /users/{user_id}` - Get specific user
- `PUT /users/{user_id}` - Update user (full_name, password)
- `POST /users/{user_id}/activate` - Activate user account
- `POST /users/{user_id}/deactivate` - Deactivate user account

### Security Implementation
- JWT tokens with HS256 algorithm
- Access tokens: 30 minutes expiration
- Refresh tokens: 7 days expiration
- Token transmission via `Authorization: Bearer <token>` header
- Password policy: min 8 chars, 1 digit, 1 uppercase, 1 lowercase
- Role-based authorization with `validate_user_for_action` method
- Admin user creation via CLI: `python -m app.domains.users.cli create-admin`
- **Note**: Endpoint protection for existing domains deferred to Phase 8

### Test Coverage
- 30 comprehensive tests covering:
  - User model properties (is_admin, is_active_and_enabled)
  - Schema validation (UserCreate, UserRegister, UserUpdate, UserLogin)
  - Repository operations (CRUD, email checks, activation/deactivation)
  - Service layer (registration, login, token management, authorization)
  - All tests passing with proper database transaction isolation

### Files Created (7 files, ~1,900 lines)
- `app/domains/users/models.py` (170 lines)
- `app/domains/users/schemas.py` (200 lines)
- `app/domains/users/repository.py` (200 lines)
- `app/domains/users/service.py` (300 lines)
- `app/domains/users/router.py` (280 lines)
- `app/domains/users/cli.py` (120 lines)
- `tests/test_users.py` (630 lines)

### Integration Points
- Updated `app/main.py` - registered auth_router and users_router
- Updated `app/core/config.py` - added INITIAL_ADMIN_EMAIL setting
- Updated `alembic/env.py` - added User model import (critical for migrations)
- Migration `36190d67d906` - created users table

---

## Phase 8: Integration & Polish ✨

**Objective**: Cross-domain integration and production readiness

**Status**: ⚪ Not Started  
**Branch**: `feature/phase-8-integration`  
**PR**: -  
**Dependencies**: All previous phases

### Tasks Checklist
- [ ] Implement cross-domain workflows
- [ ] Add comprehensive logging
- [ ] Add request/response logging middleware
- [ ] Database indexing optimization
- [ ] API documentation improvements
- [ ] Add health check endpoint with DB status
- [ ] End-to-end integration tests
- [ ] Performance testing
- [ ] Security audit
- [ ] Update all documentation
- [ ] Production deployment guide

### Cross-Domain Workflows
1. **Quote to Policy Flow**:
   - Create quote → Risk assessment → Approve → Create policy → Generate invoice

2. **Policy Lifecycle**:
   - Create → Underwrite → Approve → Activate → Bill → Renew/Cancel

3. **Payment Flow**:
   - Generate invoice → Create payment intent → Process payment → Update policy status

### Logging & Monitoring
- Structured JSON logging
- Request ID tracking
- Error tracking and reporting
- Performance metrics

### Performance Optimization
- Database query optimization
- Add missing indexes
- Connection pooling configuration
- Caching strategy (if needed)

### Documentation
- API documentation polish
- Deployment guide
- Architecture documentation
- Development setup guide

---

## 📝 Decisions Log

### 2026-04-02: Phase 3 Completion - PEP 8 Naming Compliance
- **Naming Convention**: Enforced PEP 8 Style across policy_holders domain
  - Module/Package: `policy_holders/` (lowercase_with_underscores)
  - Classes: `PolicyHolder` (CapWords/PascalCase)
  - Database tables: `policy_holders` (lowercase_with_underscores for consistency)
- **Migration Updates**: Updated migrations 001 & 002 to use `policy_holders` table
- **Relationship Fixes**: Fixed SQLAlchemy relationships between Policy and PolicyHolder
- **Import Updates**: Updated all imports from `policyholders` → `policy_holders`
- **Dependency Fix**: Added `bcrypt<4.0.0` constraint for compatibility
- **Test Coverage**: All 106 tests passing with PEP 8 compliant naming
- **Database**: PostgreSQL (relational, robust, async support)
- **ORM**: SQLAlchemy 2.0 async (flexibility, mature, not tightly coupled)
- **Architecture**: Domain-Driven Design (DDD) (clear separation of concerns)
- **Migrations**: Alembic (standard with SQLAlchemy)
- **Authentication**: JWT (stateless, scalable)
- **Payment Gateway**: Stripe (easy sandbox setup, great docs)
- **Claims Domain**: Excluded from MVP (post-MVP feature)
- **Workflow**: Each phase = 1 PR, merge only after approval

### 2026-04-02: Project Structure
- Documentation in `/docs` folder
- Implementation plan tracked in `IMPLEMENTATION_PLAN.md`
- Markdown format with checkboxes for progress tracking
- Complete detail level (phases + tasks + decisions)

---

## 🔄 PR Workflow

### Per Phase
1. Create feature branch: `feature/phase-{N}-{name}`
2. Implement all tasks for the phase
3. Write tests (unit + integration)
4. Verify locally (tests pass, docker-compose works)
5. Update this IMPLEMENTATION_PLAN.md with progress
6. Commit changes
7. Create PR on GitHub
8. Present to reviewer:
   - Executive summary of changes
   - Key code extracts
   - Link to PR
9. Wait for review and approval
10. Merge to main after approval
11. Move to next phase

### PR Template
Each PR should include:
- Phase number and name
- Summary of implemented features
- Checklist of completed tasks
- Testing evidence
- Updated documentation
- Link to updated IMPLEMENTATION_PLAN.md

---

## 📈 Progress Tracking

### Completed Phases
None yet

### Current Phase
**Phase 0: Foundation & Infrastructure** (In Progress)

### Next Phase
**Phase 1: Shared Domain Models & Enums**

---

## 🎯 Success Criteria

### Phase Completion Criteria
- ✅ All tasks checked off
- ✅ Tests written and passing (>80% coverage per module)
- ✅ Code follows style guide (ruff linting passes)
- ✅ Documentation updated
- ✅ PR reviewed and approved
- ✅ Merged to main branch
- ✅ Docker compose still works
- ✅ No breaking changes to previous phases

### MVP Completion Criteria (All Phases)
- ✅ All 9 phases completed
- ✅ Full insurance workflow functional (quote → policy → payment)
- ✅ Authentication working
- ✅ All tests passing
- ✅ API documentation complete
- ✅ Production-ready deployment config
- ✅ Performance acceptable (< 200ms avg response time)

---

## 📚 Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/)
- [Alembic Docs](https://alembic.sqlalchemy.org/)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Stripe API Docs](https://stripe.com/docs/api)

### Insurance Domain Resources
- Insurance terminology reference
- Standard policy structures
- Underwriting best practices

---

**Last Updated**: 2026-04-02  
**Maintained By**: Development Team  
**Version**: 1.0.0
