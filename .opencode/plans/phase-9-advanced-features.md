# Phase 9: Advanced Features & MVP Completion

**Status**: Post-MVP Enhancement (Optional)  
**Branch**: `feature/phase-9-advanced`  
**PR**: #11 (to be created)  
**Dependencies**: Phases 0-8  
**Last Updated**: 2026-04-03

---

## Overview

Phase 9 focuses on advanced features that enhance the core MVP (Phases 0-8):
- Claims management system
- Policy renewal workflows
- Advanced reporting and analytics
- Customer portal enhancements
- Performance optimization at scale

**Note**: This phase is OPTIONAL post-MVP. Focus on Phases 0-8 first.

---

## Phase 9A: Claims Domain (Core Feature)

### Claims Workflow
```
SUBMITTED → UNDER_REVIEW → ADDITIONAL_INFO_REQUIRED → APPROVED/REJECTED → PAID → CLOSED
```

**New Models**:
- Claim: id, policy_id, claim_number, amount_requested, amount_approved, status, description, submitted_date, created_at
- ClaimDocument: id, claim_id, document_type, file_url, uploaded_at
- ClaimHistory: id, claim_id, action, notes, user_id, created_at (audit trail)

**New Services**:
- ClaimService: submit_claim, review_claim, request_info, approve_claim, reject_claim, close_claim
- ClaimAssessmentEngine: Calculate claim payouts based on policy coverage
- NotificationService: Send emails on claim status updates

**New Endpoints**:
- POST /claims - Submit claim
- GET /claims/{id} - Get claim
- GET /claims - List claims by policy
- PUT /claims/{id}/approve - Approve claim
- PUT /claims/{id}/reject - Reject claim
- POST /claims/{id}/documents - Upload document

**File Structure**:
```
backend/app/domains/claims/
├── models.py (~250 lines)
├── schemas.py (~250 lines)
├── repository.py (~200 lines)
├── service.py (~300 lines)
├── router.py (~200 lines)
└── __init__.py (~20 lines)
```

**Scope**: ~1,200 lines + migration + 25 tests

---

## Phase 9B: Policy Renewals

### Renewal Workflow
```
Policy Status: ACTIVE → PENDING_RENEWAL (30 days before expiry)
↓
Check if eligible (all claims closed, no suspensions)
↓
Create new quote for renewal
↓
Auto-approve quote (pricing same) OR require underwriting review
↓
Create new policy
↓
Generate invoice for renewal premium
↓
Payment flow (same as new policy)
↓
New Policy Status: ACTIVE, Old Policy Status: EXPIRED
```

**New Services**:
- RenewalService: identify_due_for_renewal, create_renewal_quote, auto_renew, manual_renew_required
- Scheduled task: Daily job to check and mark policies as PENDING_RENEWAL

**Updates to Existing Models**:
- Policy: Add renewal_date, previous_policy_id (FK to self)
- Quote: Add is_renewal_quote boolean

**New Endpoints**:
- GET /policies/{id}/renewal-quote - Get renewal quote
- POST /policies/{id}/renew - Accept renewal
- GET /policies/pending-renewal - List policies needing renewal

**Implementation**: ~300 lines across service + 10 tests

---

## Phase 9C: Advanced Reporting & Analytics

### Reports

**Admin Dashboard Endpoints**:
- GET /reports/premium-revenue - Revenue by policy type, month
- GET /reports/claims-analysis - Claims by type, approval rate
- GET /reports/underwriting-stats - Underwriting performance metrics
- GET /reports/user-activity - User login/action logs
- GET /reports/policy-portfolio - Active policies breakdown

**Data Aggregation**:
```python
class ReportService:
    async def get_premium_revenue(from_date, to_date, group_by="month")
    async def get_claims_statistics(policy_type=None)
    async def get_underwriting_metrics(reviewer_id=None)
    async def get_user_activity_log(user_id=None)
    async def get_policy_portfolio_snapshot()
```

**Implementation**: ~400 lines + 10 tests

---

## Phase 9D: Notifications & Email

### Notification Service

**Events that trigger notifications**:
- User registration: Welcome email
- Policy created: Policy details email
- Underwriting review: Status change email
- Invoice created: Invoice and payment link
- Payment completed: Receipt email
- Claim submitted: Confirmation email
- Claim status change: Update email
- Policy renewal: Renewal offer email

**Implementation**:
- Email templates (Jinja2)
- EmailService (send_email, send_templated_email)
- Background jobs (async queue - optional Celery/RQ)

**Scope**: ~250 lines + templates

---

## Phase 9E: Customer Portal (Frontend)

### Enhanced Features

**Policyholder Dashboard**:
- View active policies
- View policy documents
- Pay outstanding invoices
- Submit claims
- Track claim status
- View account history
- Download statements

**Agent Dashboard**:
- Create policies and quotes
- Approve underwriting
- View assigned policies
- Generate reports
- Manage customers

**Admin Dashboard**:
- User management
- Reports and analytics
- System health monitoring
- Audit logs

**Implementation**: Frontend Next.js work, not backend

---

## Phase 9F: API Rate Limiting

### Rate Limit Implementation

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.get("/expensive-endpoint")
@limiter.limit("10/minute")
async def expensive_operation(request: Request):
    ...
```

**Rate Limits**:
- Public endpoints: 100 req/hour
- Authenticated endpoints: 1000 req/hour
- Admin endpoints: 5000 req/hour

**Scope**: ~50 lines

---

## Phase 9G: Caching Strategy

### Cache Layers

**Application-level caching** (Redis or in-memory):
```python
# Cache insurance types, coverage types (slow to change)
@cache(ttl=3600)  # 1 hour
async def get_policy_types() -> List[PolicyType]:
    ...

# Cache user roles (slow to change)
@cache(ttl=300)  # 5 minutes
async def get_user_by_id(user_id) -> User:
    ...
```

**Query result caching**:
```python
# Cache list endpoints with filters
@cache(key="policies:page={page}:status={status}", ttl=60)
async def list_policies(page, status) -> PaginatedResponse:
    ...
```

**Database query optimization**:
- Use selectinload for relationships
- Eager load nested data
- Avoid N+1 queries

**Scope**: ~150 lines + setup

---

## Phase 9H: Testing & Performance

### Load Testing
```bash
# Using locust or k6
k6 run load-test.js

# Test scenarios:
# - 100 concurrent users creating policies
# - 1000 concurrent policy views
# - Payment processing under load
```

### Performance Targets
- Homepage: < 200ms
- Policy list: < 500ms (with 10k policies)
- Quote calculation: < 100ms
- Payment processing: < 1s
- Database queries: < 100ms (95th percentile)

### Monitoring
- Add APM tool (DataDog, New Relic, or open-source Prometheus + Grafana)
- Monitor:
  - Response times by endpoint
  - Database query times
  - Error rates
  - User activity

**Scope**: ~200 lines + config

---

## Implementation Order for Phase 9

**Recommended sequence**:
1. **Phase 9A**: Claims domain (high value, core feature)
2. **Phase 9B**: Policy renewals (high value, business requirement)
3. **Phase 9C**: Reporting/analytics (stakeholder visibility)
4. **Phase 9D**: Notifications (user experience)
5. **Phase 9E**: Portal enhancements (frontend work)
6. **Phase 9F-H**: Rate limiting, caching, testing (non-critical polish)

---

## Effort Estimates

| Feature | Scope | Time | Priority |
|---------|-------|------|----------|
| Claims Domain | 1,200 lines + tests | 8 hours | High |
| Renewals | 300 lines + tests | 4 hours | High |
| Reporting | 400 lines + tests | 4 hours | Medium |
| Notifications | 250 lines + templates | 3 hours | Medium |
| Portal UX | N/A (frontend) | 8 hours | Medium |
| Rate Limiting | 50 lines | 1 hour | Low |
| Caching | 150 lines | 2 hours | Low |
| Performance Testing | 200 lines | 3 hours | Low |

**Total Phase 9**: ~24-30 hours of development

---

## Success Criteria for Phase 9

- ✅ Claims workflow fully functional
- ✅ Renewals automated and tested
- ✅ Admin can view reports
- ✅ Users receive notifications
- ✅ Load testing shows acceptable performance
- ✅ All new code tested (>80% coverage)
- ✅ Documentation updated
- ✅ System ready for production scaling

---

## MVP Completion (Phases 0-8)

After Phase 8, the MVP is COMPLETE:
- ✅ Full insurance lifecycle: Quote → Underwriting → Policy → Invoice → Payment
- ✅ Authentication & Authorization
- ✅ Role-based access control
- ✅ Comprehensive API (50+ endpoints)
- ✅ Database with 7+ tables
- ✅ 200+ passing tests
- ✅ Full documentation
- ✅ Production-ready configuration

**Phase 9** is for enhanced features beyond MVP.

---

## Decision Points

**Before starting Phase 9**:
1. Do you need claims management? (Yes → start 9A)
2. Do you need policy renewals? (Yes → start 9B)
3. Is reporting important now? (Yes → start 9C)
4. Do you want notifications? (Yes → start 9D)
5. What's the user volume expected? (High → do 9F-H)

**Recommendation**: Complete Phases 0-8 first. Phase 9 features can be added iteratively based on business needs.
