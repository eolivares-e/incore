# Insurance Core - Quick Reference

Fast lookup guide for API endpoints, statuses, roles, and common values.

---

## Table of Contents

1. [API Endpoints Summary](#api-endpoints-summary)
2. [Status Values](#status-values)
3. [Enums & Constants](#enums--constants)
4. [HTTP Status Codes](#http-status-codes)
5. [Date & Time Formats](#date--time-formats)
6. [Role Permissions Matrix](#role-permissions-matrix)

---

## API Endpoints Summary

**Base URL:** `http://localhost:8000/api/v1`

### Authentication & Users

| Method | Endpoint | Role | Purpose |
|--------|----------|------|---------|
| POST | `/auth/register` | Public | Register new user (CUSTOMER role) |
| POST | `/auth/login` | Public | Login and receive JWT tokens |
| POST | `/auth/refresh` | Public | Refresh access token |
| GET | `/auth/me` | Any | Get current authenticated user |
| PUT | `/auth/me` | Any | Update current user profile |
| POST | `/auth/logout` | Any | Logout (client-side) |
| GET | `/users` | ADMIN | List all users |
| GET | `/users/{id}` | ADMIN | Get user by ID |
| PUT | `/users/{id}/role` | ADMIN | Change user role |
| PUT | `/users/{id}/activate` | ADMIN | Activate user account |
| PUT | `/users/{id}/deactivate` | ADMIN | Deactivate user account |

### Policyholders

| Method | Endpoint | Role | Purpose |
|--------|----------|------|---------|
| POST | `/policyholders` | AGENT+ | Create new policyholder |
| GET | `/policyholders/{id}` | Any* | Get policyholder by ID |
| GET | `/policyholders` | Any* | List policyholders (paginated) |
| GET | `/policyholders/by-email/{email}` | Any | Get policyholder by email |
| PUT | `/policyholders/{id}` | AGENT+ | Update policyholder |
| DELETE | `/policyholders/{id}` | AGENT+ | Soft delete policyholder |
| POST | `/policyholders/{id}/activate` | AGENT+ | Reactivate policyholder |

**\* CUSTOMER can only access their own data**

### Policies & Coverages

| Method | Endpoint | Role | Purpose |
|--------|----------|------|---------|
| POST | `/policies` | AGENT+ | Create new policy with coverages |
| GET | `/policies/{id}` | Any* | Get policy by ID |
| GET | `/policies/number/{policy_number}` | Any* | Get policy by policy number |
| GET | `/policies` | Any* | List policies (paginated) |
| PUT | `/policies/{id}` | AGENT+ | Update policy |
| DELETE | `/policies/{id}` | AGENT+ | Soft delete policy |
| POST | `/policies/{id}/activate` | AGENT+ | Activate policy (DRAFT→ACTIVE) |
| POST | `/policies/{id}/cancel` | AGENT+ | Cancel policy |
| POST | `/policies/{policy_id}/coverages` | AGENT+ | Add coverage to policy |
| PUT | `/policies/coverages/{coverage_id}` | AGENT+ | Update coverage |
| DELETE | `/policies/coverages/{coverage_id}` | AGENT+ | Delete coverage |

### Quotes & Pricing

| Method | Endpoint | Role | Purpose |
|--------|----------|------|---------|
| POST | `/quotes` | Any | Create quote (auto-pricing) |
| GET | `/quotes/{id}` | Any* | Get quote by ID |
| GET | `/quotes/number/{quote_number}` | Any* | Get quote by quote number |
| GET | `/quotes` | Any* | List quotes (paginated) |
| PUT | `/quotes/{id}` | Any* | Update quote (DRAFT/ACTIVE only) |
| DELETE | `/quotes/{id}` | AGENT+ | Soft delete quote |
| POST | `/quotes/{id}/accept` | Any* | Accept quote |
| POST | `/quotes/{id}/reject` | AGENT+ | Reject quote |
| POST | `/pricing-rules` | ADMIN | Create pricing rule |
| GET | `/pricing-rules/{id}` | AGENT+ | Get pricing rule |
| GET | `/pricing-rules` | AGENT+ | List pricing rules |
| PUT | `/pricing-rules/{id}` | ADMIN | Update pricing rule |
| DELETE | `/pricing-rules/{id}` | ADMIN | Delete pricing rule |

### Underwriting

| Method | Endpoint | Role | Purpose |
|--------|----------|------|---------|
| POST | `/underwriting/reviews` | UNDERWRITER+ | Create underwriting review |
| GET | `/underwriting/reviews/{id}` | UNDERWRITER+ | Get review by ID |
| GET | `/underwriting/reviews` | UNDERWRITER+ | List reviews (paginated) |
| GET | `/underwriting/reviews/pending/all` | UNDERWRITER+ | Get pending reviews (by risk) |
| PUT | `/underwriting/reviews/{id}` | UNDERWRITER+ | Update review notes |
| POST | `/underwriting/reviews/{id}/approve` | UNDERWRITER+ | Approve review |
| POST | `/underwriting/reviews/{id}/reject` | UNDERWRITER+ | Reject review (notes required) |

### Billing & Payments

| Method | Endpoint | Role | Purpose |
|--------|----------|------|---------|
| POST | `/billing/invoices` | AGENT+ | Create invoice for policy |
| GET | `/billing/invoices/{id}` | Any* | Get invoice by ID |
| GET | `/billing/invoices` | Any* | List invoices (paginated) |
| GET | `/billing/invoices/policy/{policy_id}` | Any* | Get invoices for policy |
| GET | `/billing/invoices/overdue/list` | AGENT+ | Get overdue invoices |
| PATCH | `/billing/invoices/{id}` | AGENT+ | Update invoice (unpaid only) |
| DELETE | `/billing/invoices/{id}` | AGENT+ | Delete invoice (no payments) |
| POST | `/billing/payments/create-intent` | Any* | Create Stripe PaymentIntent |
| GET | `/billing/payments/{id}` | Any* | Get payment by ID |
| GET | `/billing/payments` | Any* | List payments |
| GET | `/billing/payments/invoice/{invoice_id}` | Any* | Get payments for invoice |
| POST | `/billing/payments/{id}/refund` | AGENT+ | Refund payment |
| POST | `/billing/webhooks/stripe` | Public | Stripe webhook handler |

### Workflows

| Method | Endpoint | Role | Purpose |
|--------|----------|------|---------|
| POST | `/workflows/quote-to-policy` | AGENT+ | Quote-to-policy workflow |

### Health & System

| Method | Endpoint | Role | Purpose |
|--------|----------|------|---------|
| GET | `/` | Public | Root endpoint (API info) |
| GET | `/health` | Public | Comprehensive health check |
| GET | `/health/ready` | Public | Readiness probe |
| GET | `/health/live` | Public | Liveness probe |

---

## Status Values

### Policy Statuses

| Status | Description | Terminal? |
|--------|-------------|-----------|
| `draft` | Newly created, not active | No |
| `pending_approval` | Awaiting underwriting | No |
| `active` | Policy in force | No |
| `suspended` | Temporarily inactive | No |
| `expired` | End date reached | Yes |
| `cancelled` | Manually cancelled | Yes |
| `pending_renewal` | Approaching renewal | No |

**Valid Transitions:**
- `draft` → `active`, `cancelled`
- `active` → `suspended`, `expired`, `cancelled`
- `suspended` → `active`, `cancelled`
- `pending_renewal` → `active`, `expired`

### Quote Statuses

| Status | Description | Terminal? |
|--------|-------------|-----------|
| `draft` | Initial state, being prepared | No |
| `pending` | Pending customer review | No |
| `active` | Ready for acceptance | No |
| `accepted` | Customer accepted | No |
| `rejected` | Rejected by underwriter | Yes |
| `expired` | Validity period passed | Yes |
| `converted_to_policy` | Converted to policy | Yes |

### Invoice Statuses

| Status | Description | Terminal? |
|--------|-------------|-----------|
| `draft` | Not finalized | No |
| `pending` | Awaiting payment | No |
| `sent` | Sent to customer | No |
| `paid` | Fully paid | No* |
| `overdue` | Past due date | No |
| `partially_paid` | Partial payment received | No |
| `cancelled` | Invoice cancelled | Yes |
| `refunded` | Payment refunded | Yes |

**\* Can transition to `refunded`**

### Payment Statuses

| Status | Description | Terminal? |
|--------|-------------|-----------|
| `pending` | Payment initiated | No |
| `processing` | Being processed | No |
| `completed` | Successfully completed | No* |
| `failed` | Payment failed | Yes |
| `refunded` | Fully refunded | Yes |
| `partially_refunded` | Partially refunded | No |
| `cancelled` | Payment cancelled | Yes |

**\* Can transition to `refunded` or `partially_refunded`**

### Underwriting Review Statuses

| Status | Description | Terminal? |
|--------|-------------|-----------|
| `pending` | Awaiting review | No |
| `in_review` | Being reviewed | No |
| `approved` | Review approved | Yes |
| `rejected` | Review rejected | Yes |
| `requires_manual_review` | Needs manual review | No |
| `conditionally_approved` | Approved with conditions | No |

---

## Enums & Constants

### User Roles

| Role | Hierarchy Level | Description |
|------|----------------|-------------|
| `CUSTOMER` | 1 (Lowest) | End users/policyholders |
| `AGENT` | 2 | Insurance agents |
| `UNDERWRITER` | 3 | Risk assessment staff |
| `ADMIN` | 4 (Highest) | System administrators |

**Role Hierarchy:** ADMIN > UNDERWRITER > AGENT > CUSTOMER

### Policy Types

| Type | Code | Description |
|------|------|-------------|
| Auto Insurance | `auto` | Vehicle insurance |
| Home Insurance | `home` | Property insurance |
| Life Insurance | `life` | Life coverage |
| Health Insurance | `health` | Medical coverage |

### Coverage Types

| Type | Code | Applicable Policy Types |
|------|------|------------------------|
| Liability | `liability` | Auto |
| Collision | `collision` | Auto |
| Comprehensive | `comprehensive` | Auto |
| Personal Injury Protection | `personal_injury_protection` | Auto |
| Uninsured Motorist | `uninsured_motorist` | Auto |
| Dwelling | `dwelling` | Home |
| Personal Property | `personal_property` | Home |
| Liability (Home) | `liability_home` | Home |
| Additional Living Expenses | `additional_living_expenses` | Home |
| Death Benefit | `death_benefit` | Life |
| Accidental Death | `accidental_death` | Life |
| Critical Illness | `critical_illness` | Life, Health |
| Medical | `medical` | Health |
| Dental | `dental` | Health |
| Vision | `vision` | Health |
| Prescription | `prescription` | Health |
| Mental Health | `mental_health` | Health |
| Other | `other` | All |

### Risk Levels

| Level | Risk Score Range | Auto-Approval? |
|-------|-----------------|----------------|
| `low` | 0-29 | ✅ Yes |
| `medium` | 30-69 | ⚠️ Maybe |
| `high` | 70-89 | ❌ No |
| `very_high` | 90-100 | ❌ No |

### Payment Methods

| Method | Code | Description |
|--------|------|-------------|
| Credit Card | `credit_card` | Visa, Mastercard, etc. |
| Debit Card | `debit_card` | Bank debit card |
| Bank Transfer | `bank_transfer` | ACH, wire transfer |
| Cash | `cash` | Cash payment |
| Check | `check` | Paper check |
| Digital Wallet | `digital_wallet` | Apple Pay, Google Pay |

### Gender

| Value | Code |
|-------|------|
| Male | `male` |
| Female | `female` |
| Other | `other` |
| Prefer Not to Say | `prefer_not_to_say` |

### Identification Types

| Type | Code |
|------|------|
| Driver License | `driver_license` |
| Passport | `passport` |
| National ID | `national_id` |
| SSN | `ssn` |
| Other | `other` |

---

## HTTP Status Codes

| Code | Name | Usage in API |
|------|------|--------------|
| **200** | OK | Successful GET, PUT, PATCH |
| **201** | Created | Successful POST (resource created) |
| **204** | No Content | Successful DELETE, POST /auth/logout |
| **400** | Bad Request | Validation error, malformed request |
| **401** | Unauthorized | Missing or invalid authentication token |
| **403** | Forbidden | Insufficient permissions (role-based) |
| **404** | Not Found | Resource not found |
| **422** | Unprocessable Entity | Business logic validation failed |
| **500** | Internal Server Error | Unexpected server error |
| **503** | Service Unavailable | Health check failed (DB down, etc.) |

### Common Error Response Format

```json
{
  "error": "Error message",
  "details": {
    "field": "email",
    "message": "Email already exists"
  }
}
```

**401 Unauthorized:**
```json
{
  "detail": "Could not validate credentials"
}
```

**403 Forbidden:**
```json
{
  "detail": "Insufficient permissions. Required roles: [AGENT, ADMIN]"
}
```

**404 Not Found:**
```json
{
  "error": "PolicyHolder not found",
  "details": {
    "resource": "PolicyHolder",
    "resource_id": "uuid"
  }
}
```

**422 Unprocessable Entity:**
```json
{
  "detail": [
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

---

## Date & Time Formats

### ISO 8601 Format

All dates and timestamps use **ISO 8601** format in **UTC timezone**.

**Date:**
```
YYYY-MM-DD
Example: 2026-04-03
```

**DateTime:**
```
YYYY-MM-DDTHH:MM:SSZ
Example: 2026-04-03T15:30:00Z
```

**With Milliseconds:**
```
YYYY-MM-DDTHH:MM:SS.sssZ
Example: 2026-04-03T15:30:00.123Z
```

### Common Date Fields

| Field | Type | Format | Example |
|-------|------|--------|---------|
| `created_at` | DateTime | ISO 8601 | `2026-04-03T15:30:00Z` |
| `updated_at` | DateTime | ISO 8601 | `2026-04-03T15:30:00Z` |
| `start_date` | Date | YYYY-MM-DD | `2026-05-01` |
| `end_date` | Date | YYYY-MM-DD | `2027-05-01` |
| `due_date` | Date | YYYY-MM-DD | `2026-05-02` |
| `paid_date` | Date | YYYY-MM-DD | `2026-04-15` |
| `date_of_birth` | Date | YYYY-MM-DD | `1990-01-15` |
| `valid_until` | DateTime | ISO 8601 | `2026-05-03T00:00:00Z` |

### Timezone Handling

- **Server:** All dates stored in UTC
- **Client:** Convert to local timezone for display
- **API:** Always send/receive UTC

**JavaScript Example:**
```javascript
// Parse UTC date
const utcDate = new Date('2026-04-03T15:30:00Z');

// Display in local timezone
console.log(utcDate.toLocaleString());
// Output: "4/3/2026, 11:30:00 AM" (EST)

// Send to API (convert to UTC)
const dateToSend = new Date().toISOString();
// Output: "2026-04-03T15:30:00.123Z"
```

---

## Role Permissions Matrix

### Authentication & Users

| Endpoint | CUSTOMER | AGENT | UNDERWRITER | ADMIN |
|----------|----------|-------|-------------|-------|
| POST /auth/register | ✅ | ✅ | ✅ | ✅ |
| POST /auth/login | ✅ | ✅ | ✅ | ✅ |
| GET /auth/me | ✅ | ✅ | ✅ | ✅ |
| PUT /auth/me | ✅ | ✅ | ✅ | ✅ |
| GET /users | ❌ | ❌ | ❌ | ✅ |
| PUT /users/{id}/role | ❌ | ❌ | ❌ | ✅ |

### Policyholders

| Endpoint | CUSTOMER | AGENT | UNDERWRITER | ADMIN |
|----------|----------|-------|-------------|-------|
| POST /policyholders | ❌ | ✅ | ✅ | ✅ |
| GET /policyholders/{id} | ✅* | ✅ | ✅ | ✅ |
| GET /policyholders | ✅* | ✅ | ✅ | ✅ |
| PUT /policyholders/{id} | ❌ | ✅ | ✅ | ✅ |
| DELETE /policyholders/{id} | ❌ | ✅ | ✅ | ✅ |

**\* Own data only**

### Policies

| Endpoint | CUSTOMER | AGENT | UNDERWRITER | ADMIN |
|----------|----------|-------|-------------|-------|
| POST /policies | ❌ | ✅ | ✅ | ✅ |
| GET /policies/{id} | ✅* | ✅ | ✅ | ✅ |
| GET /policies | ✅* | ✅ | ✅ | ✅ |
| PUT /policies/{id} | ❌ | ✅ | ✅ | ✅ |
| POST /policies/{id}/activate | ❌ | ✅ | ✅ | ✅ |
| POST /policies/{id}/cancel | ❌ | ✅ | ✅ | ✅ |

### Quotes

| Endpoint | CUSTOMER | AGENT | UNDERWRITER | ADMIN |
|----------|----------|-------|-------------|-------|
| POST /quotes | ✅ | ✅ | ✅ | ✅ |
| GET /quotes/{id} | ✅* | ✅ | ✅ | ✅ |
| GET /quotes | ✅* | ✅ | ✅ | ✅ |
| POST /quotes/{id}/accept | ✅* | ✅ | ✅ | ✅ |
| POST /quotes/{id}/reject | ❌ | ✅ | ✅ | ✅ |

### Pricing Rules

| Endpoint | CUSTOMER | AGENT | UNDERWRITER | ADMIN |
|----------|----------|-------|-------------|-------|
| POST /pricing-rules | ❌ | ❌ | ❌ | ✅ |
| GET /pricing-rules | ❌ | ✅ | ✅ | ✅ |
| PUT /pricing-rules/{id} | ❌ | ❌ | ❌ | ✅ |

### Underwriting

| Endpoint | CUSTOMER | AGENT | UNDERWRITER | ADMIN |
|----------|----------|-------|-------------|-------|
| POST /underwriting/reviews | ❌ | ❌ | ✅ | ✅ |
| GET /underwriting/reviews | ❌ | ❌ | ✅ | ✅ |
| POST /reviews/{id}/approve | ❌ | ❌ | ✅ | ✅ |
| POST /reviews/{id}/reject | ❌ | ❌ | ✅ | ✅ |

### Billing

| Endpoint | CUSTOMER | AGENT | UNDERWRITER | ADMIN |
|----------|----------|-------|-------------|-------|
| POST /billing/invoices | ❌ | ✅ | ✅ | ✅ |
| GET /billing/invoices/{id} | ✅* | ✅ | ✅ | ✅ |
| POST /payments/create-intent | ✅* | ✅ | ✅ | ✅ |
| POST /payments/{id}/refund | ❌ | ✅ | ✅ | ✅ |

### Workflows

| Endpoint | CUSTOMER | AGENT | UNDERWRITER | ADMIN |
|----------|----------|-------|-------------|-------|
| POST /workflows/quote-to-policy | ❌ | ✅ | ✅ | ✅ |

---

## Pagination Parameters

### Standard Parameters

| Parameter | Type | Default | Max | Description |
|-----------|------|---------|-----|-------------|
| `page` | integer | 1 | - | Page number (1-indexed) |
| `page_size` | integer | 20 | 100 | Items per page |
| `size` | integer | 10 | 100 | Items per page (alt) |
| `skip` | integer | 0 | - | Records to skip |
| `limit` | integer | 10 | 100 | Max records to return |
| `order_by` | string | - | - | Field to sort by |

### Pagination Response

```json
{
  "items": [...],
  "total": 100,
  "page": 1,
  "page_size": 20,
  "skip": 0,
  "limit": 20
}
```

---

## Token Lifetimes

| Token Type | Lifetime | Storage | Refresh Strategy |
|------------|----------|---------|------------------|
| Access Token | 30 minutes | localStorage/memory | Refresh at 25 min |
| Refresh Token | 7 days | httpOnly cookie | On expiration |

---

## Auto-Generated Fields

### Policy Number Format

```
POL-YYYY-TYPE-NNNNN
Example: POL-2026-AUTO-00001
```

- `YYYY`: Year
- `TYPE`: Policy type (AUTO, HOME, LIFE, HEALTH)
- `NNNNN`: Sequential number (5 digits)

### Quote Number Format

```
QTE-YYYY-TYPE-NNNNN
Example: QTE-2026-AUTO-00001
```

### Invoice Number Format

```
INV-YYYYMMDD-XXXX
Example: INV-20260403-0001
```

- `YYYYMMDD`: Date
- `XXXX`: Sequential number (4 digits)

---

## Business Rules

### Quote Validity

- **Duration:** 30 days from creation
- **Auto-Expiration:** Yes (daily job)
- **Can Renew:** Create new quote

### Risk Score Calculation

```
Total Risk Score = Age Risk + Coverage Risk + Policy Type Risk

Age Risk:
  < 25 years: +20
  25-35 years: +5
  35-65 years: 0
  > 65 years: +20

Coverage Risk:
  > $500k: +15
  $100k-$500k: +5
  < $100k: 0

Policy Type Risk:
  Life: +10
  Health: +8
  Auto: +5
  Home: +3
```

### Refund Eligibility

- **Time Window:** 30 days from payment
- **Status Required:** COMPLETED
- **Type:** Full refunds only (Phase 6)
- **Payment Method:** Stripe payments only

### Policy Coverage Rules

- **Minimum:** 1 coverage required
- **No Duplicates:** Same coverage type not allowed
- **Modification:** Only on DRAFT policies
- **Deletion:** Cannot delete last coverage

---

## Quick Search Tips

**Find by keyword in this file:**
- Press `Ctrl+F` (Windows/Linux) or `Cmd+F` (Mac)
- Search for endpoint, status, or enum value

**Common searches:**
- "POST /quotes" - Find quote creation endpoint
- "UNDERWRITER" - Find underwriter permissions
- "risk_level" - Find risk level values
- "401" - Find authentication error info

---

## Additional Resources

- **Main API Guide:** See `API_USER_GUIDE.md` for detailed examples
- **Workflow Diagrams:** See `WORKFLOW_DIAGRAMS.md` for visual flows
- **Postman Collection:** Import `POSTMAN_COLLECTION.json` for testing
- **Interactive API Docs:** `http://localhost:8000/api/v1/docs`

---

**Last Updated:** 2026-04-03  
**API Version:** v1  
**System:** Insurance Core
