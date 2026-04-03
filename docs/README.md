# Insurance Core API Documentation

Welcome to the Insurance Core API documentation! This folder contains comprehensive guides for integrating with and using the Insurance Core system.

---

## 📚 Documentation Files

### 1. **WORKFLOW_DIAGRAMS.md**
Visual representations of key workflows and processes using Mermaid.js diagrams.

**Contains:**
- Complete Customer Journey (end-to-end flow)
- Quote-to-Policy Workflow
- Underwriting Decision Process
- Payment Processing Flow (Stripe integration)
- Policy Status State Machine
- Authentication Flow
- Role-Based Access Control Logic
- Invoice Lifecycle

**Best for:** Understanding system flows, business processes, and state transitions.

---

### 2. **QUICK_REFERENCE.md**
Fast lookup guide for API endpoints, statuses, roles, and constants.

**Contains:**
- API Endpoints Summary (all 71 endpoints)
- Status Values (policy, quote, invoice, payment, underwriting)
- Enums & Constants (roles, policy types, coverage types, risk levels)
- HTTP Status Codes
- Date & Time Formats
- Role Permissions Matrix
- Pagination Parameters
- Auto-Generated Field Formats
- Business Rules Summary

**Best for:** Quick lookups, cheat sheet, reference during development.

---

### 3. **POSTMAN_COLLECTION.json**
Importable Postman collection with ~40 pre-configured API requests.

**Contains:**
- 8 folder structure organized by domain
- Essential endpoints for all user roles
- Pre-filled example request bodies
- Auto-extraction of tokens and IDs via test scripts
- Bearer token authentication configured
- Environment variables for easy testing

**Best for:** Testing API endpoints, exploring the API interactively, sharing with team members.

**How to Import:**
1. Open Postman
2. Click "Import" button
3. Select `POSTMAN_COLLECTION.json`
4. Collection appears in left sidebar
5. Update `baseUrl` variable if needed (default: `http://localhost:8000/api/v1`)

---

## 🚀 Quick Start

### For Frontend Developers

1. **Start Here:** Read `QUICK_REFERENCE.md` to understand:
   - Available API endpoints
   - User roles and permissions
   - Key workflows

2. **Understand Workflows:** Review `WORKFLOW_DIAGRAMS.md` to see:
   - How customers request quotes
   - Quote-to-policy conversion process
   - Payment processing with Stripe
   - Authentication flow

3. **Test the API:** Import `POSTMAN_COLLECTION.json` and:
   - Run the "00 - Setup & Auth" folder to register/login
   - Follow the folder order (01-07) for a complete workflow
   - Tokens are auto-extracted and stored

4. **Integrate:** Use the examples from the documentation to:
   - Implement authentication (JWT tokens)
   - Build quote request forms
   - Integrate Stripe payment confirmation
   - Handle role-based UI rendering

---

## 📖 Common Use Cases

### Use Case 1: Customer Self-Service Quote

**Goal:** Customer requests a quote, accepts it, and pays for the policy.

**Steps:**
1. `POST /auth/register` - Customer creates account
2. `POST /auth/login` - Customer logs in
3. Agent creates policyholder: `POST /policyholders`
4. `POST /quotes` - Customer requests quote (auto-pricing)
5. `POST /quotes/{id}/accept` - Customer accepts quote
6. `POST /billing/payments/create-intent` - Create payment
7. Frontend confirms payment via Stripe.js
8. Webhook updates payment status automatically

**See:** WORKFLOW_DIAGRAMS.md → "Complete Customer Journey"

---

### Use Case 2: Agent Creating Policy

**Goal:** Agent manually creates policy without going through quote flow.

**Steps:**
1. Agent logs in with AGENT credentials
2. `POST /policyholders` - Create policyholder record
3. `POST /policies` - Create policy with coverages (status: DRAFT)
4. `POST /policies/{id}/activate` - Activate policy (DRAFT → ACTIVE)
5. `POST /billing/invoices` - Generate invoice
6. Customer pays invoice

**See:** QUICK_REFERENCE.md → "Policies & Coverages"

---

### Use Case 3: High-Risk Underwriting Flow

**Goal:** Quote requires manual underwriting approval before policy creation.

**Steps:**
1. Customer accepts quote: `POST /quotes/{id}/accept`
2. `POST /workflows/quote-to-policy` with `skip_underwriting: false`
3. System calculates risk score (e.g., 75 = HIGH)
4. Workflow creates underwriting review (status: REQUIRES_MANUAL_REVIEW)
5. Underwriter logs in and gets pending reviews: `GET /underwriting/reviews/pending/all`
6. Underwriter approves: `POST /underwriting/reviews/{id}/approve`
7. Workflow completes: policy and invoice created

**See:** WORKFLOW_DIAGRAMS.md → "Underwriting Decision Process"

---

### Use Case 4: Processing Payment

**Goal:** Customer pays an invoice via Stripe.

**Steps:**
1. Frontend calls: `POST /billing/payments/create-intent`
2. Backend creates Stripe PaymentIntent and returns `client_secret`
3. Frontend uses Stripe.js: `stripe.confirmCardPayment(client_secret)`
4. Customer enters card details
5. Stripe processes payment and returns status to frontend
6. Stripe sends webhook to: `POST /billing/webhooks/stripe`
7. Backend updates payment status (COMPLETED) and invoice status (PAID)

**See:** WORKFLOW_DIAGRAMS.md → "Payment Processing Flow"

---

## 🔐 Authentication

### JWT Token Flow

1. **Register/Login:**
   - `POST /auth/register` or `POST /auth/login`
   - Receive `access_token` (30min) and `refresh_token` (7 days)

2. **Store Tokens:**
   - Access token: localStorage or memory
   - Refresh token: httpOnly cookie (recommended for security)

3. **Make Authenticated Requests:**
   ```http
   GET /policies
   Authorization: Bearer {access_token}
   ```

4. **Refresh Token:**
   - Before access token expires (at ~25 minutes)
   - `POST /auth/refresh` with `refresh_token`
   - Receive new `access_token`

5. **Logout:**
   - Clear all tokens from storage
   - Optionally call `POST /auth/logout`

**See:** WORKFLOW_DIAGRAMS.md → "Authentication Flow"

---

## 👥 User Roles

| Role | Level | Can Do |
|------|-------|--------|
| **CUSTOMER** | 1 | View own data, request quotes, accept quotes, pay invoices |
| **AGENT** | 2 | Full CRUD on policyholders, policies, quotes, invoices |
| **UNDERWRITER** | 3 | Review and approve/reject underwriting reviews, view quotes/policies |
| **ADMIN** | 4 | Everything + user management + pricing rules configuration |

**Hierarchy:** ADMIN > UNDERWRITER > AGENT > CUSTOMER

**Superuser:** Bypasses all role checks (full access)

**See:** QUICK_REFERENCE.md → "Role Permissions Matrix"

---

## 🔗 API Base URLs

| Environment | Base URL | Interactive Docs |
|-------------|----------|------------------|
| **Local Development** | `http://localhost:8000/api/v1` | `http://localhost:8000/docs` |
| **Docker** | `http://localhost:8000/api/v1` | `http://localhost:8000/docs` |
| **Production** | `https://api.yourcompany.com/api/v1` | `https://api.yourcompany.com/docs` |

---

## 📊 System Capabilities

The Insurance Core provides:

### Core Features
- ✅ User authentication & authorization (JWT + RBAC)
- ✅ Policyholder management
- ✅ Quote generation with auto-pricing
- ✅ Risk assessment & underwriting
- ✅ Policy & coverage management
- ✅ Billing & invoicing
- ✅ Stripe payment integration
- ✅ Cross-domain workflows

### Business Logic
- Automatic premium calculation based on risk
- Risk scoring (0-100) with auto-approval thresholds
- Quote validity period (30 days)
- Policy status state machine
- Invoice lifecycle management
- Refund processing (30-day window)

### Technical Features
- Async-first architecture (FastAPI + asyncpg)
- PostgreSQL database with composite indexes
- Structured logging (structlog)
- Request/response middleware
- Webhook support (Stripe)
- Health check endpoints
- Comprehensive validation

---

## 🎯 What's Next?

### For Backend Developers
- See `backend/CLAUDE.md` for development guidelines
- Review `backend/app/` for domain structure
- Check `backend/tests/` for test examples

### For Frontend Developers
1. Set up authentication flow (see WORKFLOW_DIAGRAMS.md)
2. Build customer portal (quotes, policies, payments)
3. Build agent dashboard (CRUD operations)
4. Build underwriter interface (review queue)
5. Build admin panel (user management, pricing rules)

### For API Consumers
- Import POSTMAN_COLLECTION.json
- Test all endpoints
- Review error responses
- Implement error handling

---

## 🐛 Troubleshooting

### Authentication Issues

**Problem:** 401 Unauthorized  
**Solution:** 
- Check if token is included in `Authorization: Bearer {token}` header
- Verify token hasn't expired (access token: 30min)
- Try refreshing token with `POST /auth/refresh`

**Problem:** 403 Forbidden  
**Solution:**
- Check user role has required permissions (see Role Permissions Matrix)
- CUSTOMER users can only access their own data
- Some endpoints require AGENT+, UNDERWRITER+, or ADMIN

### Payment Issues

**Problem:** Payment not updating invoice  
**Solution:**
- Verify Stripe webhook is configured correctly
- Check webhook endpoint: `POST /billing/webhooks/stripe`
- Ensure webhook secret is set in environment variables
- Check backend logs for webhook processing errors

**Problem:** client_secret invalid  
**Solution:**
- PaymentIntent must be created first via `/billing/payments/create-intent`
- Use the returned `client_secret` immediately (don't cache)
- Each payment requires a new PaymentIntent

### Workflow Issues

**Problem:** Quote-to-policy workflow fails  
**Solution:**
- Ensure quote status is `ACCEPTED` before running workflow
- Check quote hasn't expired (valid_until date)
- For high-risk quotes, underwriter approval may be required
- Check error response for specific failure reason

---

## 📞 Support

- **API Issues:** Check interactive docs at `/docs` or `/redoc`
- **Business Logic Questions:** Review WORKFLOW_DIAGRAMS.md
- **Integration Help:** See examples in POSTMAN_COLLECTION.json
- **Bug Reports:** File issues in project repository

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0.0** | 2026-04-03 | Initial documentation release |

---

## 📄 License

Insurance Core API Documentation  
Copyright © 2026 Insurance Core Project

---

**Happy Coding! 🚀**

For the most up-to-date information, always refer to the interactive API documentation at `/docs`.
