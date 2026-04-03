# Phase 6: Billing/Payments Domain - Implementation Guide

**Status**: Ready for Implementation  
**Branch**: `feature/phase-6-billing`  
**PR**: #8 (to be created)  
**Last Updated**: 2026-04-03

---

## Design Decisions (User Confirmed)

✅ **Invoice Number Format**: `INV-YYYYMMDD-XXXX` (e.g., INV-20260402-0001)  
✅ **Partial Payments**: Supported via `amount_paid` field tracking  
✅ **Stripe Test Mode**: Add `STRIPE_TEST_MODE: bool = True` to config  
✅ **Invoice Creation**: Manual only via API (no auto-generation)  
✅ **Stripe Payment Method**: Map to existing `CREDIT_CARD`/`DEBIT_CARD` based on card type  
✅ **Refund Time Limit**: 30 days (hardcoded in `is_refundable` property)  
✅ **Webhook Security**: Signature verification only (no IP whitelist)

---

## Implementation Checklist

### Setup Phase
- [ ] Create branch: `git checkout -b feature/phase-6-billing`
- [ ] Create directory: `mkdir -p backend/app/domains/billing`
- [ ] Add dependency to `pyproject.toml`: Add `"stripe>=8.0.0"` to dependencies list
- [ ] Install: `uv pip install -e .`

### Core Implementation (6 Files)

#### 1. Config Update
**File**: `backend/app/core/config.py`
- [ ] Add field to Settings class: `STRIPE_TEST_MODE: bool = True`

#### 2. Models
**File**: `backend/app/domains/billing/models.py` (~200 lines)

See: `phase-6-models.md` for complete implementation

Key Components:
- Invoice model: invoice_number, policy_id, amount_due, amount_paid, status
- Payment model: invoice_id, amount, stripe_payment_intent_id, status, metadata
- Properties: is_overdue, is_paid, amount_remaining, is_successful, is_refundable
- Check constraints: amounts positive, amount_paid <= amount_due
- Relationships: Invoice ↔ Policy, Invoice ↔ Payments

#### 3. Schemas
**File**: `backend/app/domains/billing/schemas.py` (~280 lines)

See: `phase-6-schemas.md` for complete implementation

12 Schemas:
- InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse, InvoiceFilterParams
- PaymentCreate, PaymentUpdate, PaymentResponse, PaymentListResponse
- StripePaymentIntentCreate, StripePaymentIntentResponse, RefundRequest

#### 4. Repository
**File**: `backend/app/domains/billing/repository.py` (~350 lines)

See: `phase-6-repository.md` for complete implementation

Key Methods:
- `generate_invoice_number()` - returns INV-YYYYMMDD-XXXX format
- `get_overdue_invoices()` - due_date < today, status != PAID
- Filter methods with pagination

#### 5. Service
**File**: `backend/app/domains/billing/service.py` (~500 lines)

See: `phase-6-service.md` for complete implementation

Classes:
- PaymentProvider (ABC) - abstract interface
- StripeProvider - Stripe SDK integration
- BillingService - invoice management
- PaymentService - payment processing, webhooks, refunds

#### 6. Router
**File**: `backend/app/domains/billing/router.py` (~320 lines)

See: `phase-6-router.md` for complete implementation

11 Endpoints - Invoice CRUD, Payment operations, Webhook

#### 7. Init File
**File**: `backend/app/domains/billing/__init__.py` (~15 lines)

See: `phase-6-init.md` for complete implementation

### Database Migration

#### 8. Create Migration
```bash
cd backend
alembic revision --autogenerate -m "add invoices and payments tables"
```

See: `phase-6-migration.md` for review checklist and manual adjustments

Then apply:
```bash
alembic upgrade head
```

### Integration

#### 9. Update Policy Model
**File**: `backend/app/domains/policies/models.py`

See: `phase-6-integration.md` for complete changes

#### 10. Register Router
**File**: `backend/app/main.py`

See: `phase-6-integration.md` for complete changes

### Testing

#### 11. Create Test Suite
**File**: `backend/tests/test_billing.py` (~450 lines, 35 tests)

See: `phase-6-tests.md` for complete implementation

Run tests:
```bash
cd backend
pytest tests/test_billing.py -v
pytest tests/ -v  # All tests (expect ~180 total)
```

### Code Quality

#### 12. Verify PEP 8 Compliance
```bash
cd backend
ruff check backend/
```

### Documentation & Git

#### 13. Update Implementation Plan
**File**: `docs/IMPLEMENTATION_PLAN.md`

Update:
- Current Phase: Phase 6 (Complete)
- Progress: 6/9 (67%)
- Phase 6 section with completion details

#### 14. Commit and Push
```bash
git add .
git status
git commit -m "feat: implement Phase 6 - Billing/Payments Domain"
git push -u origin feature/phase-6-billing
```

#### 15. Create Pull Request

See: `phase-6-pr-description.md` for complete PR body template

---

## Implementation Order

1. **Models** → Define data structure first
2. **Schemas** → Define API contracts
3. **Repository** → Data access layer
4. **Service** → Business logic (can mock Stripe initially)
5. **Router** → API endpoints
6. **Migration** → Database schema
7. **Integration** → Connect to existing domains
8. **Tests** → Full coverage with mocked Stripe

---

## Reference Files

All detailed implementations are in separate plan files:
- `phase-6-models.md` - Complete models.py code
- `phase-6-schemas.md` - Complete schemas.py code
- `phase-6-repository.md` - Complete repository.py code
- `phase-6-service.md` - Complete service.py code
- `phase-6-router.md` - Complete router.py code
- `phase-6-init.md` - Complete __init__.py code
- `phase-6-migration.md` - Migration review checklist
- `phase-6-integration.md` - Policy model and main.py changes
- `phase-6-tests.md` - Complete test suite code
- `phase-6-pr-description.md` - PR template

---

## Quick Start (New Session)

1. Read this guide
2. Review all `phase-6-*.md` files in `.opencode/plans/`
3. Follow checklist step by step
4. Implement → Test → Commit → PR

**Estimated time**: 3-4 hours for full implementation
