# Insurance Core Documentation - File Index

Quick navigation guide for all documentation files.

---

## 📂 File Structure

```
/docs
├── README.md                    ← START HERE
├── WORKFLOW_DIAGRAMS.md         ← Visual workflows
├── QUICK_REFERENCE.md           ← API cheat sheet
├── POSTMAN_COLLECTION.json      ← Test in Postman
└── INDEX.md                     ← This file
```

---

## 🎯 Where to Start

### I'm a Frontend Developer
**Start with:** `README.md` → `WORKFLOW_DIAGRAMS.md` → `POSTMAN_COLLECTION.json`

1. Read `README.md` for overview and common use cases
2. Review workflow diagrams to understand business flows
3. Import Postman collection to test API
4. Use `QUICK_REFERENCE.md` while coding

### I'm Testing the API
**Start with:** `POSTMAN_COLLECTION.json` → `README.md`

1. Import Postman collection
2. Run "00 - Setup & Auth" to get tokens
3. Follow folders 01-07 in order
4. Refer to `README.md` for troubleshooting

### I Need Specific Information
**Start with:** `QUICK_REFERENCE.md`

- Use Ctrl+F to search for endpoints, statuses, or enums
- Check role permissions matrix
- Look up HTTP status codes

### I Want to Understand Workflows
**Start with:** `WORKFLOW_DIAGRAMS.md`

- View Mermaid diagrams in GitHub/VS Code
- Understand complete customer journey
- See payment processing flow with Stripe

---

## 📖 What's in Each File

### README.md (345 lines)

**Purpose:** Main documentation index and getting started guide

**Contents:**
- Overview of all documentation files
- Quick start for frontend developers
- 4 common use cases with step-by-step examples:
  1. Customer self-service quote
  2. Agent creating policy
  3. High-risk underwriting flow
  4. Processing payment
- Authentication guide (JWT flow)
- User roles explanation
- API base URLs
- System capabilities overview
- Troubleshooting section

**When to use:** First time reading documentation, need examples, troubleshooting

---

### WORKFLOW_DIAGRAMS.md (843 lines)

**Purpose:** Visual representations of all major workflows

**Contents:** 8 Mermaid.js diagrams

1. **Complete Customer Journey** (Sequence Diagram)
   - Registration → Quote → Underwriting → Policy → Payment
   - All actors: Customer, Frontend, API, Database, Stripe, Underwriter

2. **Quote-to-Policy Workflow** (Flowchart)
   - Decision points based on risk level
   - Auto-approval vs manual review paths
   - Workflow steps and outcomes

3. **Underwriting Decision Process** (Flowchart)
   - Risk score calculation breakdown
   - Auto-approve thresholds
   - Manual review triggers

4. **Payment Processing Flow** (Sequence Diagram)
   - Stripe PaymentIntent creation
   - Frontend confirmation with Stripe.js
   - Webhook callback handling

5. **Policy Status State Machine** (State Diagram)
   - All policy statuses
   - Valid transitions
   - Terminal states

6. **Authentication Flow** (Sequence Diagram)
   - Registration, login, token refresh
   - Error handling paths
   - Token storage recommendations

7. **Role-Based Access Control** (Flowchart)
   - Permission checking logic
   - Ownership validation
   - Superuser bypass

8. **Invoice Lifecycle** (State Diagram)
   - Invoice status transitions
   - Payment triggers
   - Automatic vs manual transitions

**When to use:** Understanding business logic, explaining flows to team, planning UI

**How to view diagrams:**
- GitHub: Renders automatically
- VS Code: Install Mermaid extension
- Online: Copy to mermaid.live

---

### QUICK_REFERENCE.md (640 lines)

**Purpose:** Fast lookup guide for developers

**Contents:**

**1. API Endpoints Summary**
- All 71 endpoints organized by domain
- Table format: Method | Endpoint | Role | Purpose
- 8 sections:
  - Authentication & Users (11 endpoints)
  - Policyholders (7 endpoints)
  - Policies & Coverages (11 endpoints)
  - Quotes & Pricing (13 endpoints)
  - Underwriting (7 endpoints)
  - Billing & Payments (14 endpoints)
  - Workflows (1 endpoint)
  - Health & System (4 endpoints)

**2. Status Values**
- Policy statuses (7 values) with transitions
- Quote statuses (7 values)
- Invoice statuses (8 values)
- Payment statuses (7 values)
- Underwriting statuses (6 values)

**3. Enums & Constants**
- User roles (4) with hierarchy
- Policy types (4)
- Coverage types (18)
- Risk levels (4) with score ranges
- Payment methods (6)
- Gender (4)
- Identification types (5)

**4. HTTP Status Codes**
- Common codes (200, 201, 204, 400, 401, 403, 404, 422, 500)
- Error response format examples

**5. Date & Time Formats**
- ISO 8601 format
- Timezone handling (UTC)
- Common date fields

**6. Role Permissions Matrix**
- Complete table of endpoint permissions by role
- Grouped by domain

**7. Other References**
- Pagination parameters
- Token lifetimes
- Auto-generated field formats (policy number, quote number, invoice number)
- Business rules (quote validity, risk calculation, refunds)

**When to use:** Quick lookups while coding, checking permissions, finding status values

**Search tips:** Use Ctrl+F to find specific endpoints or values

---

### POSTMAN_COLLECTION.json (967 lines)

**Purpose:** Interactive API testing collection

**Contents:** 40 API requests organized in 8 folders

**Folders:**

1. **00 - Setup & Auth** (5 requests)
   - Register User
   - Login
   - Get Current User
   - Refresh Token
   - Logout

2. **01 - Policyholders** (4 requests)
   - Create, Get, List, Update

3. **02 - Quotes** (5 requests)
   - Create, Get, List, Accept, Reject

4. **03 - Policies** (5 requests)
   - Create, Get, List, Add Coverage, Activate

5. **04 - Underwriting** (4 requests)
   - Create Review, Get Pending, Approve, Reject

6. **05 - Billing** (5 requests)
   - Create Invoice, Get Invoice, Create Payment Intent, List Payments, Refund

7. **06 - Workflows** (1 request)
   - Quote-to-Policy Workflow

8. **07 - Admin** (3 requests)
   - Create Pricing Rule, List Users, Change User Role

9. **99 - Health** (2 requests)
   - Health Check, Readiness Check

**Features:**
- ✅ Bearer token auth auto-configured
- ✅ Environment variables (baseUrl, accessToken, refreshToken, etc.)
- ✅ Auto-extraction of IDs and tokens via test scripts
- ✅ Pre-filled example request bodies
- ✅ Organized by workflow order

**How to import:**
1. Open Postman
2. Click "Import" button
3. Select `POSTMAN_COLLECTION.json`
4. Update `baseUrl` variable if needed (default: `http://localhost:8000/api/v1`)

**Recommended workflow:**
1. Run "Register User" or "Login" in folder 00
2. Tokens are auto-saved to collection variables
3. Follow folders 01-07 in order
4. IDs are auto-extracted (policyholderId, quoteId, etc.)

**When to use:** Testing API, exploring endpoints, sharing with team, debugging

---

## 🔍 Finding Information

### Search by Topic

| What I need | Where to look |
|-------------|---------------|
| **How do I authenticate?** | README.md → Authentication section |
| **What endpoints are available?** | QUICK_REFERENCE.md → API Endpoints Summary |
| **How does the quote-to-policy flow work?** | WORKFLOW_DIAGRAMS.md → Quote-to-Policy Workflow |
| **What are the policy statuses?** | QUICK_REFERENCE.md → Status Values |
| **How do I integrate Stripe payments?** | WORKFLOW_DIAGRAMS.md → Payment Processing Flow |
| **What roles have access to X?** | QUICK_REFERENCE.md → Role Permissions Matrix |
| **How do I test the API?** | POSTMAN_COLLECTION.json → Import to Postman |
| **What are the business rules?** | QUICK_REFERENCE.md → Business Rules |
| **Example use cases?** | README.md → Common Use Cases |
| **Error response format?** | QUICK_REFERENCE.md → HTTP Status Codes |

### Search by User Role

**I'm a CUSTOMER:**
- What can I do? → README.md (User Roles section)
- How do I request a quote? → WORKFLOW_DIAGRAMS.md (Complete Customer Journey)
- How do I pay? → WORKFLOW_DIAGRAMS.md (Payment Processing Flow)

**I'm an AGENT:**
- What permissions do I have? → QUICK_REFERENCE.md (Role Permissions Matrix)
- How do I create policies? → README.md (Use Case 2)
- Test API → POSTMAN_COLLECTION.json (folders 01-03, 05)

**I'm an UNDERWRITER:**
- How does underwriting work? → WORKFLOW_DIAGRAMS.md (Underwriting Decision Process)
- What's the review process? → README.md (Use Case 3)
- Test API → POSTMAN_COLLECTION.json (folder 04)

**I'm an ADMIN:**
- What can I configure? → QUICK_REFERENCE.md (Admin endpoints)
- How do pricing rules work? → POSTMAN_COLLECTION.json (folder 07)
- User management → README.md (User Roles)

---

## 📊 Documentation Statistics

| Metric | Value |
|--------|-------|
| Total Files | 4 |
| Total Lines | 2,795 |
| Total Size | ~88 KB |
| Endpoints Documented | 40 essential (71 total available) |
| Workflow Diagrams | 8 |
| Use Case Examples | 4 |
| User Roles Covered | All 4 (CUSTOMER, AGENT, UNDERWRITER, ADMIN) |

---

## ✅ Checklist for Frontend Developers

- [ ] Read README.md
- [ ] Review WORKFLOW_DIAGRAMS.md (at least Customer Journey and Payment Flow)
- [ ] Import POSTMAN_COLLECTION.json and test authentication
- [ ] Bookmark QUICK_REFERENCE.md for lookups
- [ ] Test a complete workflow in Postman (folders 00-03)
- [ ] Understand role-based permissions
- [ ] Review Stripe payment integration flow
- [ ] Implement JWT token management in frontend
- [ ] Handle error responses (401, 403, 404, 422)

---

## 🚀 Next Steps

1. **For immediate API testing:** Import `POSTMAN_COLLECTION.json`
2. **For understanding workflows:** Read `WORKFLOW_DIAGRAMS.md`
3. **For development reference:** Bookmark `QUICK_REFERENCE.md`
4. **For examples:** See `README.md` use cases

---

## 📞 Getting Help

- **Can't find something?** Use Ctrl+F within each file
- **Diagram not rendering?** View on GitHub or use mermaid.live
- **API errors?** Check README.md → Troubleshooting
- **Business logic questions?** See WORKFLOW_DIAGRAMS.md

---

**Documentation Version:** 1.0.0  
**Last Updated:** 2026-04-03  
**System:** Insurance Core API v1
