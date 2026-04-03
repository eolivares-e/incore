# Insurance Core - Workflow Diagrams

Visual representations of key workflows and processes in the Insurance Core system.

---

## Table of Contents

1. [Complete Customer Journey](#1-complete-customer-journey)
2. [Quote-to-Policy Workflow](#2-quote-to-policy-workflow)
3. [Underwriting Decision Process](#3-underwriting-decision-process)
4. [Payment Processing Flow](#4-payment-processing-flow)
5. [Policy Status State Machine](#5-policy-status-state-machine)
6. [Authentication Flow](#6-authentication-flow)
7. [Role-Based Access Control](#7-role-based-access-control)
8. [Invoice Lifecycle](#8-invoice-lifecycle)

---

## 1. Complete Customer Journey

**Description:** End-to-end flow from user registration to active policy with payment.

```mermaid
sequenceDiagram
    participant C as Customer
    participant F as Frontend
    participant API as Backend API
    participant DB as Database
    participant S as Stripe
    participant U as Underwriter

    %% Registration
    C->>F: Register Account
    F->>API: POST /auth/register
    API->>DB: Create User (CUSTOMER)
    DB-->>API: User Created
    API-->>F: UserResponse + Tokens
    F-->>C: Welcome Message

    %% Agent Creates Policyholder
    Note over F,API: Agent creates policyholder profile
    F->>API: POST /policyholders
    API->>DB: Create Policyholder
    DB-->>API: Policyholder Created
    API-->>F: PolicyholderResponse

    %% Quote Request
    C->>F: Request Quote
    F->>API: POST /quotes
    API->>API: Calculate Premium & Risk
    API->>DB: Save Quote
    DB-->>API: Quote Created
    API-->>F: QuoteResponse (premium, risk_level)
    F-->>C: Show Quote Details

    %% Accept Quote
    C->>F: Accept Quote
    F->>API: POST /workflows/quote-to-policy
    
    %% Underwriting
    API->>DB: Create Underwriting Review
    API->>API: Calculate Risk Score
    
    alt Low Risk (score < 30)
        API->>DB: Auto-Approve
        API->>DB: Create Policy (ACTIVE)
    else High Risk (score >= 70)
        API->>DB: Set Status: REQUIRES_MANUAL_REVIEW
        U->>API: GET /underwriting/reviews/pending/all
        API-->>U: Pending Reviews
        U->>API: POST /underwriting/reviews/{id}/approve
        API->>DB: Create Policy (ACTIVE)
    end

    %% Invoice & Payment
    API->>DB: Create Invoice
    API->>DB: Update Quote Status
    DB-->>API: Workflow Complete
    API-->>F: WorkflowResponse (policy, invoice)
    
    F->>API: POST /billing/payments/create-intent
    API->>S: Create PaymentIntent
    S-->>API: client_secret
    API->>DB: Create Payment (PENDING)
    API-->>F: PaymentIntentResponse
    
    F->>S: Confirm Payment (Stripe.js)
    S-->>F: Payment Success
    S->>API: Webhook: payment_intent.succeeded
    API->>DB: Update Payment (COMPLETED)
    API->>DB: Update Invoice (PAID)
    
    F-->>C: Policy Active!
```

**Key Steps:**
1. **Registration** - Customer creates account (CUSTOMER role)
2. **Policyholder Creation** - Agent creates policyholder profile with personal details
3. **Quote Request** - Customer requests insurance quote, system calculates premium and risk
4. **Quote Acceptance** - Customer accepts quote, triggers workflow
5. **Underwriting Review** - Automated risk assessment with optional manual review
6. **Policy Creation** - Policy created with ACTIVE status upon approval
7. **Invoice Generation** - Invoice created automatically with 30-day due date
8. **Payment Processing** - Customer pays via Stripe, webhook confirms payment
9. **Active Policy** - Customer is now covered

---

## 2. Quote-to-Policy Workflow

**Description:** Detailed workflow for converting an accepted quote into an active policy.

```mermaid
flowchart TD
    Start([POST /workflows/quote-to-policy]) --> ValidateQuote{Quote Status<br/>= ACCEPTED?}
    
    ValidateQuote -->|No| Error1[Return Error:<br/>Quote not accepted]
    ValidateQuote -->|Yes| CheckSkip{skip_underwriting<br/>= true?}
    
    CheckSkip -->|Yes| SkipUW[Skip Underwriting]
    CheckSkip -->|No| CreateUW[Create Underwriting Review]
    
    CreateUW --> CalcRisk[Calculate Risk Score<br/>0-100 scale]
    CalcRisk --> RiskCheck{Risk Score?}
    
    RiskCheck -->|< 30<br/>LOW| AutoApprove[Auto-Approve]
    RiskCheck -->|30-69<br/>MEDIUM| InReview[Status: IN_REVIEW<br/>May auto-approve]
    RiskCheck -->|>= 70<br/>HIGH/VERY_HIGH| ManualReview[Status: REQUIRES_MANUAL_REVIEW<br/>Wait for underwriter]
    
    ManualReview --> UWDecision{Underwriter<br/>Decision}
    UWDecision -->|Approve| ApprovedPath[Underwriting Approved]
    UWDecision -->|Reject| Rejected[Return Error:<br/>Underwriting rejected]
    
    AutoApprove --> ApprovedPath
    InReview --> ApprovedPath
    SkipUW --> ApprovedPath
    
    ApprovedPath --> CreatePolicy[Create Policy<br/>Status: ACTIVE]
    CreatePolicy --> AddCoverages[Add Default Coverages<br/>Based on Policy Type]
    AddCoverages --> UpdateQuote[Update Quote Status<br/>CONVERTED_TO_POLICY]
    UpdateQuote --> CreateInvoice[Create Invoice<br/>Due: +30 days]
    CreateInvoice --> Success([Return Success Response])
    
    style Start fill:#e1f5e1
    style Success fill:#e1f5e1
    style Error1 fill:#ffe1e1
    style Rejected fill:#ffe1e1
    style AutoApprove fill:#fff4e1
    style ManualReview fill:#ffe1e1
```

**Workflow Steps:**

1. **Validate Quote** - Must be in ACCEPTED status
2. **Check Underwriting Skip** - Can skip for low-risk scenarios
3. **Create Underwriting Review** - If not skipped
4. **Calculate Risk Score** - 0-100 based on age, coverage, policy type
5. **Risk-Based Decision**:
   - LOW (< 30): Auto-approve immediately
   - MEDIUM (30-69): May auto-approve or require review
   - HIGH/VERY_HIGH (>= 70): Requires manual underwriter approval
6. **Create Policy** - Only if approved, status = ACTIVE
7. **Add Coverages** - Default coverages based on policy type
8. **Update Quote** - Status = CONVERTED_TO_POLICY
9. **Create Invoice** - Due date = 30 days from now
10. **Return Response** - Comprehensive workflow result

**Response Includes:**
- Quote details and new status
- Underwriting review ID and decision
- Risk score and level
- Policy ID and number
- Invoice ID and amount
- Workflow timing metrics

---

## 3. Underwriting Decision Process

**Description:** How risk assessment and underwriting decisions are made.

```mermaid
flowchart TD
    Start([Create Underwriting Review]) --> Input[Input Data:<br/>- Quote/Policy<br/>- Policyholder Info]
    
    Input --> CalcRisk[Calculate Risk Score]
    
    CalcRisk --> AgeRisk[Age Risk Factor<br/>< 25 or > 65: +20<br/>25-35: +5<br/>35-65: 0]
    CalcRisk --> CoverageRisk[Coverage Risk Factor<br/>> $500k: +15<br/>$100k-$500k: +5<br/>< $100k: 0]
    CalcRisk --> TypeRisk[Policy Type Risk<br/>Life: +10<br/>Auto: +5<br/>Home: +3<br/>Health: +8]
    
    AgeRisk --> SumRisk[Total Risk Score<br/>Sum all factors]
    CoverageRisk --> SumRisk
    TypeRisk --> SumRisk
    
    SumRisk --> RiskLevel{Determine<br/>Risk Level}
    
    RiskLevel -->|0-29| Low[LOW Risk<br/>Auto-Approve]
    RiskLevel -->|30-69| Medium[MEDIUM Risk<br/>In Review]
    RiskLevel -->|70-89| High[HIGH Risk<br/>Manual Review Required]
    RiskLevel -->|90-100| VeryHigh[VERY HIGH Risk<br/>Senior Underwriter Required]
    
    Low --> ApproveAuto[Status: APPROVED<br/>approved_at: now]
    
    Medium --> MediumDecision{Policy Type<br/>& Amount}
    MediumDecision -->|Auto<br/>< $100k| ApproveAuto
    MediumDecision -->|Life/Health<br/>or > $100k| QueueReview[Status: IN_REVIEW<br/>Queue for underwriter]
    
    High --> QueueManual[Status: REQUIRES_MANUAL_REVIEW<br/>Assign to underwriter]
    VeryHigh --> QueueSenior[Status: REQUIRES_MANUAL_REVIEW<br/>Flag for senior underwriter]
    
    QueueReview --> UWAction1{Underwriter<br/>Action}
    QueueManual --> UWAction2{Underwriter<br/>Action}
    QueueSenior --> UWAction2
    
    UWAction1 -->|Approve| ManualApprove[Status: APPROVED<br/>reviewer_id: underwriter<br/>approved_at: now]
    UWAction1 -->|Reject| ManualReject[Status: REJECTED<br/>reviewer_id: underwriter<br/>rejected_at: now<br/>notes: REQUIRED]
    
    UWAction2 -->|Approve| ManualApprove
    UWAction2 -->|Reject| ManualReject
    
    ApproveAuto --> End1([Proceed to Policy Creation])
    ManualApprove --> End1
    ManualReject --> End2([Stop Workflow<br/>Notify Customer])
    
    style Low fill:#e1f5e1
    style Medium fill:#fff4e1
    style High fill:#ffe8cc
    style VeryHigh fill:#ffe1e1
    style ApproveAuto fill:#e1f5e1
    style ManualApprove fill:#e1f5e1
    style ManualReject fill:#ffe1e1
    style End1 fill:#e1f5e1
    style End2 fill:#ffe1e1
```

**Risk Score Calculation:**

| Factor | Condition | Points |
|--------|-----------|--------|
| **Age** | < 25 years old | +20 |
| | 25-35 years old | +5 |
| | 35-65 years old | 0 |
| | > 65 years old | +20 |
| **Coverage Amount** | > $500,000 | +15 |
| | $100,000 - $500,000 | +5 |
| | < $100,000 | 0 |
| **Policy Type** | Life Insurance | +10 |
| | Health Insurance | +8 |
| | Auto Insurance | +5 |
| | Home Insurance | +3 |

**Risk Levels:**

- **LOW (0-29)**: Auto-approve immediately
- **MEDIUM (30-69)**: May require review based on policy type
- **HIGH (70-89)**: Always requires manual review
- **VERY HIGH (90-100)**: Requires senior underwriter approval

---

## 4. Payment Processing Flow

**Description:** Stripe payment integration from invoice to payment confirmation.

```mermaid
sequenceDiagram
    participant C as Customer
    participant F as Frontend
    participant API as Backend API
    participant DB as Database
    participant S as Stripe

    Note over F,API: Invoice already exists

    %% Create Payment Intent
    C->>F: Click "Pay Invoice"
    F->>API: POST /billing/payments/create-intent<br/>{invoice_id, amount}
    API->>DB: Get Invoice Details
    DB-->>API: Invoice Data
    
    API->>S: Create PaymentIntent<br/>{amount, currency: USD, metadata}
    S-->>API: {payment_intent_id, client_secret, status}
    
    API->>DB: Create Payment Record<br/>Status: PENDING<br/>stripe_payment_intent_id
    DB-->>API: Payment Created
    
    API-->>F: {client_secret, payment_intent_id}
    
    %% Frontend Payment Confirmation
    F->>F: Initialize Stripe.js<br/>with client_secret
    F->>C: Show Payment Form<br/>(Card details)
    C->>F: Enter Card Info & Submit
    
    F->>S: stripe.confirmCardPayment(client_secret)
    S->>S: Process Payment
    
    alt Payment Successful
        S-->>F: {status: "succeeded"}
        F-->>C: "Payment Successful!"
        
        %% Webhook Updates
        S->>API: Webhook: payment_intent.succeeded<br/>{payment_intent_id}
        API->>DB: Find Payment by stripe_payment_intent_id
        API->>DB: Update Payment Status: COMPLETED<br/>paid_at: now
        API->>DB: Update Invoice amount_paid<br/>Check if fully paid
        
        alt Invoice Fully Paid
            API->>DB: Update Invoice Status: PAID<br/>paid_date: now
        else Partially Paid
            API->>DB: Update Invoice Status: PARTIALLY_PAID
        end
        
        API-->>S: 200 OK (Webhook ACK)
        
    else Payment Failed
        S-->>F: {status: "failed", error}
        F-->>C: "Payment Failed: {error}"
        
        S->>API: Webhook: payment_intent.payment_failed
        API->>DB: Update Payment Status: FAILED
        API-->>S: 200 OK
    end
    
    Note over F,API: Frontend can poll<br/>GET /billing/payments/{id}<br/>to confirm status
```

**Payment Flow Steps:**

1. **Create PaymentIntent**
   - Backend creates Stripe PaymentIntent
   - Backend creates Payment record (status: PENDING)
   - Returns `client_secret` to frontend

2. **Frontend Confirmation**
   - Initialize Stripe.js with `client_secret`
   - Customer enters payment details
   - Call `stripe.confirmCardPayment()`

3. **Stripe Processing**
   - Stripe processes the payment
   - Returns success/failure to frontend immediately

4. **Webhook Update** (Asynchronous)
   - Stripe sends webhook to backend
   - Backend updates Payment status (COMPLETED/FAILED)
   - Backend updates Invoice amount_paid
   - If fully paid, Invoice status → PAID

5. **Confirmation**
   - Frontend shows success/failure message
   - Can poll payment status for confirmation

**Key Points:**
- Payment status updates are asynchronous (webhook-driven)
- Frontend receives immediate feedback from Stripe
- Backend updates happen via webhook (reliable, secure)
- Invoice automatically marked PAID when fully paid
- Supports partial payments (Phase 6)

---

## 5. Policy Status State Machine

**Description:** Valid policy statuses and allowed transitions.

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Create Policy

    DRAFT --> ACTIVE: Activate Policy<br/>(POST /policies/{id}/activate)
    DRAFT --> CANCELLED: Cancel Draft<br/>(POST /policies/{id}/cancel)
    
    ACTIVE --> SUSPENDED: Suspend Policy<br/>(Non-payment, fraud)
    ACTIVE --> EXPIRED: End Date Reached<br/>(Automatic)
    ACTIVE --> CANCELLED: Cancel Active Policy<br/>(POST /policies/{id}/cancel)
    
    SUSPENDED --> ACTIVE: Reactivate<br/>(Payment received)
    SUSPENDED --> CANCELLED: Cancel Suspended<br/>(Grace period expired)
    
    PENDING_RENEWAL --> ACTIVE: Renew Policy<br/>(Future: renewal workflow)
    PENDING_RENEWAL --> EXPIRED: Not Renewed<br/>(Automatic)
    
    EXPIRED --> [*]: End of Lifecycle
    CANCELLED --> [*]: End of Lifecycle
    
    note right of DRAFT
        Initial state when created.
        Can modify coverages.
        No billing.
    end note
    
    note right of ACTIVE
        Policy is in force.
        Customer is covered.
        Billing is active.
    end note
    
    note right of SUSPENDED
        Temporarily inactive.
        Common: non-payment.
        Can be reactivated.
    end note
    
    note right of EXPIRED
        End date reached.
        Terminal state.
        Cannot reactivate.
    end note
    
    note right of CANCELLED
        Manually cancelled.
        Terminal state.
        Refund may apply.
    end note
```

**Status Descriptions:**

| Status | Description | Can Modify? | Billing Active? |
|--------|-------------|-------------|-----------------|
| **DRAFT** | Newly created, not yet active | ✅ Yes | ❌ No |
| **PENDING_APPROVAL** | Awaiting underwriting approval | ❌ No | ❌ No |
| **ACTIVE** | Policy in force, customer covered | ❌ No | ✅ Yes |
| **SUSPENDED** | Temporarily inactive (e.g., non-payment) | ❌ No | ⚠️ Paused |
| **EXPIRED** | End date reached, coverage ended | ❌ No | ❌ No |
| **CANCELLED** | Manually cancelled before expiration | ❌ No | ❌ No |
| **PENDING_RENEWAL** | Approaching end date, renewal available | ❌ No | ✅ Yes |

**Allowed Transitions:**

| From | To | Trigger | Role Required |
|------|----|---------|--------------| 
| DRAFT | ACTIVE | Manual activation | AGENT+ |
| DRAFT | CANCELLED | Manual cancellation | AGENT+ |
| ACTIVE | SUSPENDED | Non-payment detected | SYSTEM/AGENT+ |
| ACTIVE | EXPIRED | End date reached | SYSTEM (automatic) |
| ACTIVE | CANCELLED | Manual cancellation | AGENT+ |
| SUSPENDED | ACTIVE | Payment received | SYSTEM/AGENT+ |
| SUSPENDED | CANCELLED | Grace period expired | AGENT+ |
| PENDING_RENEWAL | ACTIVE | Renewal completed | AGENT+ |
| PENDING_RENEWAL | EXPIRED | Not renewed | SYSTEM (automatic) |

**Business Rules:**
- Only DRAFT policies can have coverages added/removed
- ACTIVE policies generate invoices
- EXPIRED and CANCELLED are terminal states (no further transitions)
- Automatic transitions happen via scheduled jobs (not implemented in Phase 8)

---

## 6. Authentication Flow

**Description:** User authentication, token management, and session lifecycle.

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant API as Backend API
    participant DB as Database

    %% Registration
    rect rgb(230, 245, 230)
        note right of U: Registration Flow
        U->>F: Register (email, password, full_name)
        F->>API: POST /auth/register
        API->>API: Validate email format<br/>Check password strength
        API->>DB: Check email uniqueness
        
        alt Email Exists
            DB-->>API: Email found
            API-->>F: 400 Error: Email exists
            F-->>U: "Email already registered"
        else Email Available
            DB-->>API: Email available
            API->>API: Hash password (bcrypt)
            API->>DB: Create User (role: CUSTOMER)
            DB-->>API: User created
            API->>API: Generate JWT tokens<br/>access (30min)<br/>refresh (7 days)
            API-->>F: {user, access_token, refresh_token}
            F->>F: Store tokens<br/>(localStorage/cookie)
            F-->>U: "Welcome! Registration successful"
        end
    end

    %% Login
    rect rgb(230, 235, 245)
        note right of U: Login Flow
        U->>F: Login (email, password)
        F->>API: POST /auth/login
        API->>DB: Find user by email
        
        alt User Not Found
            DB-->>API: No user
            API-->>F: 401 Error: Invalid credentials
            F-->>U: "Invalid email or password"
        else User Found
            DB-->>API: User data
            API->>API: Verify password hash
            
            alt Password Invalid
                API-->>F: 401 Error: Invalid credentials
                F-->>U: "Invalid email or password"
            else Password Valid
                alt User Inactive
                    API-->>F: 403 Error: Account disabled
                    F-->>U: "Account is disabled"
                else User Active
                    API->>API: Generate JWT tokens
                    API-->>F: {access_token, refresh_token}
                    F->>F: Store tokens
                    F-->>U: "Login successful"
                end
            end
        end
    end

    %% Authenticated Request
    rect rgb(245, 240, 230)
        note right of U: Making Authenticated Request
        U->>F: Access Protected Resource
        F->>API: GET /policies<br/>Authorization: Bearer {access_token}
        API->>API: Verify JWT signature<br/>Check expiration<br/>Extract user_id & role
        
        alt Token Expired
            API-->>F: 401 Error: Token expired
            F->>F: Attempt token refresh
            F->>API: POST /auth/refresh<br/>{refresh_token}
            
            alt Refresh Valid
                API->>API: Verify refresh token
                API->>API: Generate new access token
                API-->>F: {access_token}
                F->>F: Store new access token
                F->>API: Retry: GET /policies<br/>New access token
                API->>DB: Fetch policies
                DB-->>API: Policy data
                API-->>F: Policy list
                F-->>U: Show policies
            else Refresh Invalid/Expired
                API-->>F: 401 Error: Refresh token invalid
                F->>F: Clear all tokens
                F-->>U: Redirect to login
            end
            
        else Token Valid
            API->>DB: Fetch policies<br/>(filtered by role & ownership)
            DB-->>API: Policy data
            API-->>F: Policy list
            F-->>U: Show policies
        end
    end

    %% Logout
    rect rgb(245, 230, 230)
        note right of U: Logout Flow
        U->>F: Logout
        F->>F: Clear tokens from storage
        F->>API: POST /auth/logout (optional)
        API-->>F: 204 No Content
        F-->>U: Redirect to login page
    end
```

**Token Details:**

| Token Type | Lifetime | Storage | Use |
|------------|----------|---------|-----|
| **Access Token** | 30 minutes | localStorage or memory | API authentication |
| **Refresh Token** | 7 days | httpOnly cookie (recommended) | Token refresh |

**Token Payload (JWT):**
```json
{
  "sub": "user-uuid",
  "email": "user@example.com",
  "role": "CUSTOMER",
  "is_superuser": false,
  "exp": 1735689600,
  "iat": 1735688000
}
```

**Security Best Practices:**
1. Store access token in memory or localStorage
2. Store refresh token in httpOnly cookie (prevents XSS)
3. Always use HTTPS in production
4. Implement token refresh before expiration (e.g., at 25 minutes)
5. Clear all tokens on logout
6. Never log tokens
7. Implement rate limiting on auth endpoints

---

## 7. Role-Based Access Control

**Description:** Permission checking and ownership validation logic.

```mermaid
flowchart TD
    Start([API Request]) --> HasToken{Authorization<br/>Header?}
    
    HasToken -->|No| Public{Endpoint<br/>Public?}
    Public -->|Yes| AllowPublic[Allow Access]
    Public -->|No| Deny401[401 Unauthorized<br/>"Missing token"]
    
    HasToken -->|Yes| VerifyToken[Verify JWT Token]
    VerifyToken --> TokenValid{Token Valid?}
    
    TokenValid -->|No| Deny401B[401 Unauthorized<br/>"Invalid token"]
    TokenValid -->|Yes| ExtractUser[Extract user_id & role]
    
    ExtractUser --> CheckActive{User<br/>is_active?}
    CheckActive -->|No| Deny403A[403 Forbidden<br/>"Account disabled"]
    CheckActive -->|Yes| CheckSuper{is_superuser?}
    
    CheckSuper -->|Yes| AllowSuper[✅ Allow All<br/>Bypass role checks]
    CheckSuper -->|No| CheckRole{Endpoint<br/>Role Requirement}
    
    CheckRole -->|None Required| AllowAuth[Allow Access]
    CheckRole -->|ADMIN| IsAdmin{User role<br/>= ADMIN?}
    CheckRole -->|UNDERWRITER+| IsUnderwriter{User role in<br/>[UNDERWRITER, ADMIN]?}
    CheckRole -->|AGENT+| IsAgent{User role in<br/>[AGENT, UNDERWRITER, ADMIN]?}
    
    IsAdmin -->|No| Deny403B[403 Forbidden<br/>"Admin role required"]
    IsAdmin -->|Yes| AllowRole[Allow Access]
    
    IsUnderwriter -->|No| Deny403C[403 Forbidden<br/>"Underwriter role required"]
    IsUnderwriter -->|Yes| AllowRole
    
    IsAgent -->|No| Deny403D[403 Forbidden<br/>"Agent role required"]
    IsAgent -->|Yes| AllowRole
    
    AllowAuth --> CheckOwnership{Ownership<br/>Validation?}
    AllowRole --> CheckOwnership
    
    CheckOwnership -->|Not Required| Execute[Execute Endpoint]
    CheckOwnership -->|Required| IsCustomer{User role<br/>= CUSTOMER?}
    
    IsCustomer -->|No| Execute
    IsCustomer -->|Yes| OwnsResource{User owns<br/>resource?}
    
    OwnsResource -->|No| Deny403E[403 Forbidden<br/>"Access denied"]
    OwnsResource -->|Yes| Execute
    
    Execute --> Success([200/201 Response])
    
    style AllowPublic fill:#e1f5e1
    style AllowSuper fill:#e1f5e1
    style AllowAuth fill:#e1f5e1
    style AllowRole fill:#e1f5e1
    style Execute fill:#e1f5e1
    style Success fill:#e1f5e1
    style Deny401 fill:#ffe1e1
    style Deny401B fill:#ffe1e1
    style Deny403A fill:#ffe1e1
    style Deny403B fill:#ffe1e1
    style Deny403C fill:#ffe1e1
    style Deny403D fill:#ffe1e1
    style Deny403E fill:#ffe1e1
```

**Role Hierarchy:**

```
ADMIN (Highest)
  ↓
UNDERWRITER
  ↓
AGENT
  ↓
CUSTOMER (Lowest)
```

**Permission Matrix:**

| Endpoint | CUSTOMER | AGENT | UNDERWRITER | ADMIN |
|----------|----------|-------|-------------|-------|
| POST /auth/register | ✅ Public | ✅ Public | ✅ Public | ✅ Public |
| GET /policyholders/{id} | ✅ Own only | ✅ All | ✅ All | ✅ All |
| POST /policyholders | ❌ | ✅ | ✅ | ✅ |
| POST /quotes | ✅ Own | ✅ All | ✅ All | ✅ All |
| POST /quotes/{id}/accept | ✅ Own | ✅ All | ✅ All | ✅ All |
| POST /policies | ❌ | ✅ | ✅ | ✅ |
| POST /underwriting/reviews | ❌ | ❌ | ✅ | ✅ |
| POST /billing/invoices | ❌ | ✅ | ✅ | ✅ |
| POST /pricing-rules | ❌ | ❌ | ❌ | ✅ |
| POST /users/{id}/role | ❌ | ❌ | ❌ | ✅ |

**Ownership Validation:**

For CUSTOMER role, access is restricted to:
- Policyholders where `user_id = current_user.id`
- Policies owned by their policyholders
- Quotes owned by their policyholders
- Invoices for their policies
- Payments for their invoices

**Superuser:**
- Bypasses ALL role and ownership checks
- Full access to all resources
- Typically system admin accounts

---

## 8. Invoice Lifecycle

**Description:** Invoice status transitions from creation to payment/cancellation.

```mermaid
stateDiagram-v2
    [*] --> DRAFT: Create Invoice<br/>(Manual creation)
    [*] --> PENDING: Create Invoice<br/>(Workflow auto-creation)

    DRAFT --> PENDING: Finalize Draft
    DRAFT --> CANCELLED: Cancel Draft

    PENDING --> SENT: Send to Customer<br/>(Email notification)
    PENDING --> PAID: Full Payment Received<br/>(amount_paid = amount_due)
    PENDING --> OVERDUE: Due Date Passed<br/>(Automatic)
    PENDING --> PARTIALLY_PAID: Partial Payment<br/>(amount_paid < amount_due)
    PENDING --> CANCELLED: Cancel Invoice

    SENT --> PAID: Full Payment Received
    SENT --> OVERDUE: Due Date Passed
    SENT --> PARTIALLY_PAID: Partial Payment
    SENT --> CANCELLED: Cancel Invoice

    OVERDUE --> PAID: Late Payment Received
    OVERDUE --> PARTIALLY_PAID: Partial Payment
    OVERDUE --> CANCELLED: Write Off

    PARTIALLY_PAID --> PAID: Remaining Payment Received
    PARTIALLY_PAID --> OVERDUE: Due Date Passed<br/>(Still unpaid)
    PARTIALLY_PAID --> REFUNDED: Refund Partial Payment

    PAID --> REFUNDED: Refund Issued<br/>(Full or Partial)

    REFUNDED --> [*]: End of Lifecycle
    PAID --> [*]: End of Lifecycle
    CANCELLED --> [*]: End of Lifecycle

    note right of DRAFT
        Initial state (rare).
        Can be edited.
        Not sent to customer.
    end note

    note right of PENDING
        Most common initial state.
        Awaiting payment.
        Customer can pay.
    end note

    note right of SENT
        Email/notification sent.
        Awaiting payment.
    end note

    note right of OVERDUE
        Past due date.
        May trigger late fees.
        Policy may suspend.
    end note

    note right of PAID
        Fully paid.
        Terminal state (unless refund).
    end note

    note right of REFUNDED
        Payment refunded.
        Terminal state.
    end note
```

**Status Descriptions:**

| Status | Description | amount_paid | amount_remaining |
|--------|-------------|-------------|------------------|
| **DRAFT** | Not finalized, editable | 0 | amount_due |
| **PENDING** | Awaiting payment | 0 | amount_due |
| **SENT** | Notification sent to customer | 0 | amount_due |
| **PAID** | Fully paid | amount_due | 0 |
| **OVERDUE** | Past due date, unpaid | 0 or partial | > 0 |
| **PARTIALLY_PAID** | Some payment received | > 0 | > 0 |
| **CANCELLED** | Invoice cancelled | any | any |
| **REFUNDED** | Payment refunded | varies | varies |

**Automatic Transitions:**

| Trigger | From | To | Timing |
|---------|------|----|--------|
| Payment completed | PENDING/SENT/OVERDUE | PAID | Immediate (webhook) |
| Partial payment | PENDING/SENT/OVERDUE | PARTIALLY_PAID | Immediate (webhook) |
| Due date passed | PENDING/SENT | OVERDUE | Daily job (midnight) |
| Refund issued | PAID | REFUNDED | Immediate (API call) |

**Business Rules:**

1. **Payment Processing:**
   - Each successful payment updates `amount_paid`
   - If `amount_paid >= amount_due`, status → PAID
   - If `0 < amount_paid < amount_due`, status → PARTIALLY_PAID

2. **Overdue Detection:**
   - Runs daily at midnight
   - Checks all invoices with `due_date < today` and status in [PENDING, SENT]
   - Updates status to OVERDUE

3. **Refunds:**
   - Only PAID invoices can be refunded
   - Full refund: `amount_paid = 0`, status → REFUNDED
   - Partial refund: `amount_paid -= refund_amount`, status → PARTIALLY_PAID

4. **Cancellation:**
   - Can cancel DRAFT, PENDING, SENT, OVERDUE, PARTIALLY_PAID
   - Cannot cancel PAID or REFUNDED (use refund instead)

---

## Summary

These diagrams represent the core workflows in the Insurance Core system:

1. **Customer Journey** - Complete end-to-end flow
2. **Quote-to-Policy** - Automated conversion workflow
3. **Underwriting** - Risk assessment and approval process
4. **Payment** - Stripe integration flow
5. **Policy Status** - Policy lifecycle state machine
6. **Authentication** - User auth and token management
7. **RBAC** - Role-based access control logic
8. **Invoice Lifecycle** - Invoice status transitions

All diagrams use Mermaid.js syntax and can be rendered in:
- GitHub markdown preview
- VS Code with Mermaid extension
- GitLab, Notion, Obsidian
- Online: mermaid.live

For more details on API endpoints and request/response formats, see the main API User Guide.
