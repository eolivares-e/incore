# Complete Insurance Core Implementation Plan - All Phases

**Project**: Insurance Core (incore)  
**Status**: Phases 0-5 Complete, Phase 6 Ready, Phases 7-9 Planned  
**Last Updated**: 2026-04-03

---

## Executive Summary

Insurance Core is a 9-phase implementation of a complete insurance management system. We are currently at **Phase 5 Complete (Underwriting)**, with Phase 6 (Billing) ready to implement and Phases 7-9 planned.

### Completed Phases (5/9 = 56%)
- ✅ Phase 0: Foundation & Infrastructure
- ✅ Phase 1: Shared Domain Models & Enums
- ✅ Phase 2: Policyholders Domain
- ✅ Phase 3: Policies Domain
- ✅ Phase 4: Pricing/Quoting Domain
- ✅ Phase 5: Underwriting Domain (PR #7 - MERGED)

### Ready to Implement (In Order)
- ⏳ Phase 6: Billing/Payments Domain (Planning docs complete)
- ⏳ Phase 7: Authentication & Authorization (Planning docs complete)
- ⏳ Phase 8: Integration & Polish (Planning docs complete)
- ⏳ Phase 9: Advanced Features (Optional post-MVP)

---

## Quick Start Guide

### For Phase 6 (Billing/Payments)
```bash
cd /home/xiyoh/Projects/incore

# Read the planning documents
cat .opencode/plans/phase-6-main-guide.md
cat .opencode/plans/phase-6-models.md
ls .opencode/plans/phase-6-*.md

# Start implementation
git checkout -b feature/phase-6-billing
# Follow checklist in phase-6-main-guide.md
```

### For Phase 7 (Authentication)
```bash
# After Phase 6 is merged
git checkout -b feature/phase-7-auth
cat .opencode/plans/phase-7-main-guide.md
# Follow checklist
```

### For Phase 8 (Integration & Polish)
```bash
# After Phase 7 is merged
git checkout -b feature/phase-8-integration
cat .opencode/plans/phase-8-main-guide.md
# Follow checklist
```

### For Phase 9 (Optional Advanced Features)
```bash
# After Phase 8 is complete
cat .opencode/plans/phase-9-advanced-features.md
# Choose which features to implement
```

---

## All Planning Documents Created

### Main Guides (Ready to Use)
- `.opencode/plans/phase-6-main-guide.md` - Complete Phase 6 checklist
- `.opencode/plans/phase-7-main-guide.md` - Complete Phase 7 checklist
- `.opencode/plans/phase-8-main-guide.md` - Complete Phase 8 checklist
- `.opencode/plans/phase-9-advanced-features.md` - Optional Phase 9 features

### Phase 6 Detail Documents (Ready)
- `.opencode/plans/phase-6-summary.md` - Quick reference
- `.opencode/plans/phase-6-models.md` - ✅ Complete models.py code

### Phase 6 Detail Documents (To Create)
- `phase-6-schemas.md` - 12 Pydantic schemas with validators
- `phase-6-repository.md` - Invoice/Payment repositories
- `phase-6-service.py.md` - Stripe integration + business logic
- `phase-6-router.md` - 11 API endpoints
- `phase-6-tests.md` - 35 tests with mocked Stripe
- `phase-6-migration.md` - Migration review checklist
- `phase-6-integration.md` - Config + Policy model + main.py changes
- `phase-6-pr-description.md` - PR template

### Phase 7 Detail Documents (To Create)
- `phase-7-models.md` - User model code
- `phase-7-schemas.md` - Auth schemas code
- `phase-7-service.md` - AuthService code
- `phase-7-router.md` - Auth endpoints code
- `phase-7-tests.md` - Auth tests code
- `phase-7-pr-description.md` - PR template

### Phase 8 & 9 (Documented in Guides)
- All content included in main guide files
- No separate detail documents needed (more about integration than new code)

---

## Project Statistics

### Current State (End of Phase 5)
- **Backend Files**: 50+ files
- **Lines of Code**: ~3,500 lines (backend)
- **Database Tables**: 7 (policy_holders, policies, coverages, quotes, pricing_rules, underwriting_reviews)
- **API Endpoints**: 40+
- **Tests**: 145 passing
- **Test Coverage**: >80% per module
- **Migrations**: 4 completed + 1 in progress

### After Phase 6 (Billing)
- **New Endpoints**: +11 (Invoice, Payment, Webhook)
- **New Tables**: +2 (invoices, payments)
- **New Tests**: +35
- **New Lines**: ~2,100

### After Phase 7 (Auth)
- **New Endpoints**: +11 (Register, Login, Refresh, User mgmt)
- **New Tables**: +1 (users)
- **New Tests**: +30
- **New Lines**: ~1,520

### After Phase 8 (Integration)
- **Integration Tests**: +30
- **Documentation**: +500 lines
- **New Lines**: ~1,500 (mostly tests + docs)

### MVP Complete (Phases 0-8)
- **Total Backend Lines**: ~8,600
- **Total Endpoints**: 90+
- **Total Tables**: 10
- **Total Tests**: 240+
- **Total Coverage**: >85%

### Phase 9 (Optional)
- Claims: +1,200 lines
- Renewals: +300 lines
- Reporting: +400 lines
- Other: +500 lines
- **Total Additional**: ~2,400 lines

---

## Architecture Overview

### Tech Stack
```
Backend: FastAPI + Python 3.12 (async)
Database: PostgreSQL 16 (async with SQLAlchemy 2.0 + asyncpg)
ORM: SQLAlchemy 2.0
Migrations: Alembic
Testing: pytest + pytest-asyncio
Auth: JWT (Phase 7)
Payments: Stripe (Phase 6)
```

### Domain Structure (DDD Pattern)
```
backend/app/domains/
├── policy_holders/        (Phase 2) ✅
├── policies/              (Phase 3) ✅
├── pricing/               (Phase 4) ✅
├── underwriting/          (Phase 5) ✅
├── billing/               (Phase 6) ⏳
├── users/                 (Phase 7) ⏳
└── claims/                (Phase 9) ❓

Each domain:
├── models.py          - SQLAlchemy models
├── schemas.py         - Pydantic schemas
├── repository.py      - Data access
├── service.py         - Business logic
├── router.py          - API endpoints
└── __init__.py        - Public exports
```

### Database Schema (Current)
```
Tables: 7
- policy_holders (id, email, name, age, gender, etc.)
- policies (id, policy_number, policyholder_id, policy_type, status, dates)
- coverages (id, policy_id, coverage_type, limit, deductible)
- quotes (id, quote_number, policyholder_id, policy_type, premium, status)
- pricing_rules (id, rule_type, min_age, max_age, multiplier)
- underwriting_reviews (id, quote_id/policy_id, reviewer_id, risk_score, status)

Adding in Phase 6:
- invoices (id, invoice_number, policy_id, amount, status)
- payments (id, invoice_id, amount, stripe_id, status)

Adding in Phase 7:
- users (id, email, hashed_password, role, is_superuser)

Adding in Phase 9 (optional):
- claims (id, claim_number, policy_id, amount, status)
- claim_documents (id, claim_id, file_url)
- claim_history (id, claim_id, action, notes, user_id)
```

### API Endpoints (Current: 40+, After MVP: 90+)

**By Phase**:
- Phase 2: 6 endpoints (policyholders CRUD)
- Phase 3: 8 endpoints (policies + coverage CRUD)
- Phase 4: 8 endpoints (quotes + pricing rules CRUD)
- Phase 5: 8 endpoints (underwriting reviews CRUD + approval)
- Phase 6: 11 endpoints (invoices + payments + webhook)
- Phase 7: 11 endpoints (auth + user management)
- Phase 8: +1 (health check + tracking)
- Phase 9: +15 (claims, renewals, reports)

---

## Phase Details

### Phase 0: Foundation & Infrastructure ✅
**Status**: COMPLETE (PR #1)
- FastAPI setup
- PostgreSQL + SQLAlchemy
- Alembic migrations
- JWT token utilities
- Password hashing utilities
- Exception handling framework
- CORS configuration

### Phase 1: Shared Domain Models & Enums ✅
**Status**: COMPLETE (PR #3)
- PolicyStatus, PolicyType, ClaimStatus, PaymentStatus, PaymentMethod enums
- CoverageType, Gender, RiskLevel, IdentificationType enums
- UnderwritingStatus, QuoteStatus, InvoiceStatus enums
- Base schemas and types
- Pagination support

### Phase 2: Policyholders Domain ✅
**Status**: COMPLETE (PR #4)
- PolicyHolder model with validation
- 6 CRUD endpoints
- Full test coverage
- PEP 8 compliance enforced

### Phase 3: Policies Domain ✅
**Status**: COMPLETE (PR #5)
- Policy + Coverage models
- 8 CRUD endpoints
- Relationship to PolicyHolder
- Auto-generation of policy numbers
- Full test coverage

### Phase 4: Pricing/Quoting Domain ✅
**Status**: COMPLETE (PR #6)
- Quote + PricingRule models
- Quote acceptance workflow
- PricingEngine with risk assessment
- 8 CRUD endpoints
- Full test coverage

### Phase 5: Underwriting Domain ✅
**Status**: COMPLETE (PR #7 - MERGED)
- UnderwritingReview model
- Auto-approval logic (risk_score < 30)
- Manual review workflow (risk_score >= 70)
- RiskScoringEngine (quote-based, policy-based)
- 8 CRUD + workflow endpoints
- 22 comprehensive tests
- Full test coverage

### Phase 6: Billing/Payments Domain ⏳
**Status**: READY TO IMPLEMENT
- Invoice + Payment models
- Partial payment support (amount_paid tracking)
- Stripe integration with webhooks
- PaymentProvider interface + StripeProvider
- 11 endpoints (invoice CRUD, payment intent, webhook)
- 35 comprehensive tests
- Invoice number generation (INV-YYYYMMDD-XXXX)
- 30-day refund window

**Planning Documents Created**: ✅
- Main guide with complete checklist
- Models implementation (complete code)

**Planning Documents Needed**:
- Schemas, repository, service, router (code)
- Tests, migration, integration, PR description

### Phase 7: Authentication & Authorization ⏳
**Status**: PLANNED
- User model with roles (ADMIN, UNDERWRITER, AGENT, CUSTOMER)
- JWT token issuance + refresh
- Password hashing + strength validation
- Login/register endpoints
- Protected endpoints with Depends(get_current_user)
- Role-based access control (RBAC)
- 11 auth + user management endpoints
- 30 comprehensive tests

**Planning Documents Created**: ✅
- Complete main guide with implementation details
- Design decisions documented

### Phase 8: Integration & Polish ⏳
**Status**: PLANNED
- Cross-domain workflow testing
- Quote → Policy → Invoice → Payment flow
- Structured JSON logging
- Request tracing middleware
- Health check endpoint
- Database index optimization
- Comprehensive documentation
- Integration tests (30+)
- E2E tests (10+)

**Planning Documents Created**: ✅
- Complete main guide with all integration points
- No code needed (mostly integration + testing)

### Phase 9: Advanced Features ❓
**Status**: OPTIONAL POST-MVP
- Claims domain (claim submission, approval, payment workflow)
- Policy renewal automation
- Advanced reporting + analytics
- Email notifications
- Customer portal enhancements
- Rate limiting
- Caching strategy
- Load testing + performance optimization

**Planning Documents Created**: ✅
- Complete overview with effort estimates

---

## Implementation Status

### Ready to Start
- ✅ Phase 6 (Billing) - Planning complete, can start now

### Planning Complete
- ✅ Phase 7 (Auth) - Ready after Phase 6
- ✅ Phase 8 (Integration) - Ready after Phase 7
- ✅ Phase 9 (Optional) - Ready after Phase 8

### Testing Status
- Phase 0-5: 145 tests passing ✅
- Phase 6: 35 tests ready to write
- Phase 7: 30 tests ready to write
- Phase 8: 30+ integration tests ready to write
- Phase 9: 25+ tests per feature

---

## Key Documents

### Main Documentation
- `docs/IMPLEMENTATION_PLAN.md` - (in repo) Main implementation tracking
- `CLAUDE.md` - (in repo) Claude/AI assistant guidelines

### Planning Documents (in `.opencode/plans/`)
- `phase-6-main-guide.md` - Billing phase complete guide ✅
- `phase-6-models.md` - Models code ready ✅
- `phase-6-summary.md` - Quick reference ✅
- `phase-7-main-guide.md` - Auth phase complete guide ✅
- `phase-8-main-guide.md` - Integration phase guide ✅
- `phase-9-advanced-features.md` - Optional features guide ✅

---

## How to Continue

### Next Session

1. **Read Quick Start**:
   ```bash
   cat .opencode/plans/phase-6-summary.md
   ```

2. **Review Full Phase 6 Plan**:
   ```bash
   cat .opencode/plans/phase-6-main-guide.md
   ```

3. **Check Models Code** (already written):
   ```bash
   cat .opencode/plans/phase-6-models.md
   ```

4. **Ask AI to Complete Detail Files**:
   - Request: "Create phase-6-schemas.md with complete code"
   - Repeat for: repository, service, router, tests, migration, integration, PR description

5. **Start Implementation**:
   - Create branch
   - Follow checklist step by step
   - Test thoroughly
   - Create PR

### After Phase 6

1. Review Phase 7 guide
2. Ask AI to create detail files if needed
3. Implement Phase 7
4. Review Phase 8 guide
5. Implement Phase 8 (mostly integration + testing)

### Completion Targets

**MVP Complete (Phases 0-8)**: ~3-4 weeks
- Phase 6: 4-5 days (billing implementation)
- Phase 7: 3-4 days (auth implementation)
- Phase 8: 5-7 days (integration + testing)

**Full System (+ Phase 9)**: +2-3 weeks additional
- Claims: 2-3 days
- Renewals: 1-2 days
- Reporting: 1-2 days
- Other features: 2-3 days

---

## Success Criteria

### By End of Phase 6
- ✅ Billing system fully functional
- ✅ Stripe integration tested
- ✅ Invoices auto-generated from policies
- ✅ Payments processed and tracked
- ✅ Webhooks receiving Stripe events
- ✅ 35 new tests passing
- ✅ ~180 total tests passing
- ✅ PR reviewed and merged

### By End of Phase 7 (MVP Auth)
- ✅ User registration + login working
- ✅ JWT tokens issued and refreshed
- ✅ All endpoints protected
- ✅ Role-based access enforced
- ✅ 30 new tests passing
- ✅ ~210 total tests passing

### By End of Phase 8 (MVP Complete)
- ✅ Full workflow: Quote → Policy → Invoice → Payment
- ✅ 30+ integration tests passing
- ✅ Logging + monitoring working
- ✅ Documentation complete
- ✅ Performance acceptable (< 200ms avg)
- ✅ Security audit passed
- ✅ Ready for production
- ✅ ~240+ total tests passing

### By End of Phase 9 (Full System)
- ✅ Claims management working
- ✅ Policy renewals automated
- ✅ Reporting available
- ✅ Notifications sending
- ✅ Load testing passed
- ✅ ~100+ endpoint coverage
- ✅ >90% test coverage
- ✅ Production ready at scale

---

## Important Notes

### Before Starting Phase 6
- Ensure Phase 5 is fully merged to main
- All 145 tests passing
- Docker compose working
- Stripe test account credentials ready

### Design Decisions Made
All decisions documented in respective phase guides. Key ones:
- **Invoice numbering**: INV-YYYYMMDD-XXXX format
- **Partial payments**: Supported via amount_paid field
- **Stripe test mode**: Configurable toggle
- **User roles**: ADMIN, UNDERWRITER, AGENT, CUSTOMER
- **Auth pattern**: JWT with access + refresh tokens
- **Cross-domain**: Orchestrated via WorkflowService

### Code Quality
- All code follows PEP 8 (enforced by ruff)
- >80% test coverage per module
- DDD architecture maintained
- Type hints on all functions
- Comprehensive docstrings

---

## Questions or Issues?

If you encounter questions while implementing:
1. Check phase-specific main guide
2. Review implementation detail files (phase-X-*.md)
3. Check existing domains for patterns (policies, pricing, underwriting)
4. Run tests frequently to catch issues early
5. Consult CLAUDE.md for project guidelines

---

## Summary

**You are here**: Phase 5 Complete, Phase 6 Ready to Implement

**Next 3 Months**:
- Week 1-2: Phase 6 (Billing)
- Week 2-3: Phase 7 (Auth)
- Week 3-4: Phase 8 (Integration & Polish)
- **MVP Complete!**

**Optional**:
- Week 4-5: Phase 9 (Advanced Features)
- **Full System Complete!**

All planning documents are ready. Time to implement! 🚀
