# Phase 6: Quick Reference Summary

**For New Session Context**

---

## What We've Accomplished So Far

### Phases Complete (5/9 = 56%)
- ✅ Phase 0: Foundation & Infrastructure
- ✅ Phase 1: Shared Domain Models & Enums
- ✅ Phase 2: Policyholders Domain
- ✅ Phase 3: Policies Domain
- ✅ Phase 4: Pricing/Quoting Domain
- ✅ Phase 5: Underwriting Domain (PR #7 - MERGED)

### Current Status
- **Branch**: `main` (up to date)
- **Latest Commit**: Phase 5 merged
- **Tests**: 145 passing
- **Next**: Phase 6 - Billing/Payments Domain

---

## Phase 6: What's Next

### Goal
Implement complete billing and payment system with Stripe integration

### Design Decisions (User Confirmed)
1. ✅ Invoice numbering: `INV-YYYYMMDD-XXXX`
2. ✅ Partial payments: Supported
3. ✅ Stripe test mode: Configurable toggle
4. ✅ Manual invoice creation only
5. ✅ Stripe → CREDIT_CARD/DEBIT_CARD mapping
6. ✅ 30-day refund window
7. ✅ Webhook signature verification only

### Implementation Files Created
All detailed plans are in `.opencode/plans/`:

**Main Guide**:
- `phase-6-main-guide.md` - Complete checklist and overview

**Detailed Implementation** (to be created):
- `phase-6-models.md` - ✅ CREATED (Invoice, Payment models)
- `phase-6-schemas.md` - TODO (12 schemas)
- `phase-6-repository.md` - TODO (CRUD + filters)
- `phase-6-service.md` - TODO (Stripe integration, business logic)
- `phase-6-router.md` - TODO (11 endpoints)
- `phase-6-tests.md` - TODO (35 tests with mocked Stripe)
- `phase-6-migration.md` - TODO (Review checklist)
- `phase-6-integration.md` - TODO (Policy model, main.py)
- `phase-6-pr-description.md` - TODO (PR template)

### Scope Summary
- **Files to create**: 7 files (~1,665 lines)
- **Files to modify**: 4 files (config, policies/models, main, pyproject.toml)
- **Tests**: 35 new tests (~450 lines)
- **Migration**: 005 (2 tables, 11 indexes, 4 constraints)
- **Dependency**: stripe>=8.0.0

---

## Next Steps

### To Start Phase 6 Implementation:

1. **Read** `.opencode/plans/phase-6-main-guide.md`
2. **Review** all `phase-6-*.md` files
3. **Create** branch: `git checkout -b feature/phase-6-billing`
4. **Follow** checklist step by step
5. **Test** thoroughly with mocked Stripe
6. **Create** PR #8

### Quick Commands
```bash
# Start
cd /home/xiyoh/Projects/incore
git checkout main
git pull
git checkout -b feature/phase-6-billing

# Review plans
cat .opencode/plans/phase-6-main-guide.md
ls .opencode/plans/phase-6-*.md

# After implementation
pytest tests/test_billing.py -v
git add .
git commit -m "feat: implement Phase 6 - Billing/Payments Domain"
git push -u origin feature/phase-6-billing
gh pr create
```

---

## Remaining Work for Complete Phase 6 Plans

Still need to create these detailed plan files:
- [ ] `phase-6-schemas.md` - 12 Pydantic schemas
- [ ] `phase-6-repository.md` - Invoice/Payment repositories
- [ ] `phase-6-service.md` - Business logic + Stripe provider
- [ ] `phase-6-router.md` - 11 API endpoints
- [ ] `phase-6-tests.md` - Test suite with fixtures
- [ ] `phase-6-migration.md` - Migration review guide
- [ ] `phase-6-integration.md` - Integration changes
- [ ] `phase-6-pr-description.md` - PR template

**Status**: Models complete, 8 more files to document

---

## Context for AI Assistant (Next Session)

"We've completed Phase 5 (Underwriting) and merged it to main. Now implementing Phase 6 (Billing/Payments) with Stripe integration. User confirmed all design decisions. I've created the main guide and models implementation. Please complete the remaining 8 detailed plan files in `.opencode/plans/` so the user can implement Phase 6 step-by-step."

**Current files**:
- `.opencode/plans/phase-6-main-guide.md` - ✅ Complete checklist
- `.opencode/plans/phase-6-models.md` - ✅ Complete models code
- `.opencode/plans/phase-6-summary.md` - ✅ This file

**Needed**:
Complete documentation for: schemas, repository, service, router, tests, migration, integration, PR description

**Constraint**: Read-only mode - only create plan files in `.opencode/plans/`, no implementation yet
