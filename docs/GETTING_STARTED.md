# Getting Started with Insurance Core API

**5-Minute Quick Start Guide**

This guide will get you up and running with the Insurance Core API in 5 minutes.

---

## Prerequisites

- ✅ Docker and Docker Compose installed
- ✅ Postman or similar API client (optional)
- ✅ Basic understanding of REST APIs
- ✅ Basic understanding of JWT authentication

---

## Step 1: Start the System (1 minute)

```bash
# From project root
docker-compose up

# Wait for all services to start...
# Backend will be available at: http://localhost:8000
# Frontend will be available at: http://localhost:3000
```

**Verify it's running:**
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "checks": {
    "database": "ok",
    "api": "ok"
  }
}
```

---

## Step 2: Explore Interactive API Docs (1 minute)

Open your browser and go to:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

You can test ALL endpoints directly from the browser!

---

## Step 3: Create Your First User (1 minute)

### Option A: Using cURL

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "full_name": "Test User"
  }'
```

### Option B: Using Swagger UI

1. Go to http://localhost:8000/docs
2. Find `POST /auth/register`
3. Click "Try it out"
4. Enter:
   ```json
   {
     "email": "test@example.com",
     "password": "SecurePass123!",
     "full_name": "Test User"
   }
   ```
5. Click "Execute"

**Save the tokens from the response:**
```json
{
  "id": "uuid-here",
  "email": "test@example.com",
  "full_name": "Test User",
  "role": "CUSTOMER",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbG...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbG..."
}
```

---

## Step 4: Make Your First Authenticated Request (1 minute)

Get your user profile:

```bash
# Replace {access_token} with your actual token
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer {access_token}"
```

Or in Swagger UI:
1. Click the "Authorize" button (🔒 icon at top)
2. Enter: `Bearer {access_token}`
3. Click "Authorize"
4. Now all requests will include your token!
5. Try `GET /auth/me`

---

## Step 5: Import Postman Collection (1 minute)

**Faster testing with Postman:**

1. Open Postman
2. Click "Import"
3. Select `docs/POSTMAN_COLLECTION.json`
4. Collection appears with 40 pre-configured requests
5. Update the `accessToken` variable with your token
6. Start testing!

**Pro tip:** The collection auto-extracts tokens when you login, so you don't have to copy/paste them!

---

## Complete Example Workflow

Let's create a quote, accept it, and see a policy created!

### 1. Login (if you haven't already)

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!"
  }'
```

Save the `access_token`.

### 2. Create a Policyholder

**Note:** You'll need an AGENT role for this. For testing, create an admin user using the CLI:

```bash
# In docker:
docker-compose exec backend python -m app.domains.users.cli create-user \
  --email agent@example.com \
  --password SecurePass123! \
  --full-name "Agent User" \
  --role AGENT
```

Then login as the agent and create a policyholder:

```bash
curl -X POST http://localhost:8000/api/v1/policyholders \
  -H "Authorization: Bearer {agent_access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "phone": "+1-555-123-4567",
    "date_of_birth": "1990-01-15",
    "gender": "male",
    "street_address": "123 Main St",
    "city": "New York",
    "state": "NY",
    "zip_code": "10001",
    "country": "USA",
    "identification_type": "driver_license",
    "identification_number": "DL123456789"
  }'
```

Save the `id` from the response.

### 3. Create a Quote

```bash
curl -X POST http://localhost:8000/api/v1/quotes \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "policy_holder_id": "{policyholder_id}",
    "policy_type": "auto",
    "requested_coverage_amount": 500000.00,
    "notes": "Customer wants comprehensive auto insurance"
  }'
```

**Response includes auto-calculated premium and risk level!**

```json
{
  "id": "quote-uuid",
  "quote_number": "QTE-2026-AUTO-00001",
  "calculated_premium": 1200.00,
  "risk_level": "medium",
  "risk_score": 45,
  "valid_until": "2026-05-03T00:00:00Z",
  "status": "active",
  ...
}
```

Save the `id`.

### 4. Accept the Quote

```bash
curl -X POST http://localhost:8000/api/v1/quotes/{quote_id}/accept \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Quote is now accepted and can be converted to a policy!**

### 5. Convert to Policy Using Workflow

```bash
curl -X POST http://localhost:8000/api/v1/workflows/quote-to-policy \
  -H "Authorization: Bearer {agent_access_token}" \
  -H "Content-Type: application/json" \
  -d '{
    "quote_id": "{quote_id}",
    "skip_underwriting": false
  }'
```

**Response includes:**
- ✅ Underwriting review (auto-approved if low/medium risk)
- ✅ Policy created (with ACTIVE status)
- ✅ Invoice created (with 30-day due date)
- ✅ Complete workflow timing

```json
{
  "success": true,
  "message": "Quote successfully converted to policy",
  "quote_id": "...",
  "quote_status": "converted_to_policy",
  "underwriting_decision": "approved",
  "risk_score": 45,
  "policy_id": "...",
  "policy_number": "POL-2026-AUTO-00001",
  "policy_status": "active",
  "invoice_id": "...",
  "invoice_amount": 1200.00,
  "total_duration_seconds": 2.5
}
```

**You now have an active insurance policy! 🎉**

---

## What You Just Did

1. ✅ Started the Insurance Core system
2. ✅ Created a user account with JWT authentication
3. ✅ Made authenticated API requests
4. ✅ Created a policyholder (customer record)
5. ✅ Generated a quote with auto-pricing and risk assessment
6. ✅ Converted quote to active policy using workflow
7. ✅ Got an invoice ready for payment

---

## Next Steps

### For Frontend Developers

1. **Understand the workflows:**
   - Read `docs/WORKFLOW_DIAGRAMS.md`
   - See visual diagrams of all processes

2. **Build the customer portal:**
   - Login/registration page
   - Quote request form
   - Policy view dashboard
   - Payment integration (Stripe)

3. **Build the agent dashboard:**
   - Policyholder CRUD
   - Policy management
   - Quote generation
   - Invoice creation

4. **Build the underwriter interface:**
   - Review queue (pending high-risk quotes)
   - Approve/reject reviews
   - Risk assessment dashboard

5. **Reference documentation:**
   - `docs/README.md` - Use cases and examples
   - `docs/QUICK_REFERENCE.md` - API endpoint reference
   - `docs/POSTMAN_COLLECTION.json` - Testing collection

### For Backend Developers

1. Review `backend/CLAUDE.md` for:
   - Development guidelines
   - Domain structure
   - Testing strategy
   - PEP 8 compliance

2. Explore the codebase:
   - `backend/app/domains/` - Domain-driven design
   - `backend/app/workflows/` - Cross-domain workflows
   - `backend/tests/` - Test examples

### For API Integrators

1. **Import Postman collection:**
   - Test all endpoints interactively
   - See example requests/responses
   - Auto-token management

2. **Review error handling:**
   - See `docs/QUICK_REFERENCE.md` → HTTP Status Codes
   - Implement proper error handling in your client

3. **Understand authentication:**
   - JWT token lifecycle
   - Refresh token strategy
   - Role-based permissions

---

## Common Issues

### Issue: 401 Unauthorized

**Cause:** Missing or expired access token

**Solution:**
```bash
# Get a new access token
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "{your_refresh_token}"
  }'
```

### Issue: 403 Forbidden

**Cause:** Insufficient permissions (role-based)

**Solution:**
- Check user role: `GET /auth/me`
- Some endpoints require AGENT+, UNDERWRITER+, or ADMIN
- Create users with appropriate roles using CLI (see Step 2 in workflow)

### Issue: Docker services not starting

**Solution:**
```bash
# Stop and remove all containers
docker-compose down -v

# Rebuild and start fresh
docker-compose up --build
```

### Issue: Database migrations not applied

**Solution:**
```bash
# From backend directory
docker-compose exec backend alembic upgrade head
```

---

## Useful Commands

### Create Users with Different Roles

```bash
# Create AGENT user
docker-compose exec backend python -m app.domains.users.cli create-user \
  --email agent@example.com \
  --password SecurePass123! \
  --full-name "Agent User" \
  --role AGENT

# Create UNDERWRITER user
docker-compose exec backend python -m app.domains.users.cli create-user \
  --email underwriter@example.com \
  --password SecurePass123! \
  --full-name "Underwriter User" \
  --role UNDERWRITER

# Create ADMIN user
docker-compose exec backend python -m app.domains.users.cli create-user \
  --email admin@example.com \
  --password SecurePass123! \
  --full-name "Admin User" \
  --role ADMIN \
  --superuser
```

### View Logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Check Database

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U insurance_user -d insurance_core

# List tables
\dt

# Query policyholders
SELECT * FROM policy_holders;

# Exit
\q
```

### Run Backend Tests

```bash
# From backend directory
docker-compose exec backend pytest tests/ -v

# With coverage
docker-compose exec backend pytest tests/ --cov=app --cov-report=html
```

---

## API Documentation Links

Once system is running:

- **Interactive API Docs (Swagger):** http://localhost:8000/docs
- **Alternative Docs (ReDoc):** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health
- **Root Endpoint:** http://localhost:8000/

---

## Additional Resources

- **Complete API Reference:** `docs/QUICK_REFERENCE.md`
- **Workflow Diagrams:** `docs/WORKFLOW_DIAGRAMS.md`
- **Use Case Examples:** `docs/README.md`
- **Postman Collection:** `docs/POSTMAN_COLLECTION.json`
- **Development Guide:** `backend/CLAUDE.md`

---

## Support

- **API Issues:** Check `/docs` interactive documentation
- **Business Logic Questions:** Review `WORKFLOW_DIAGRAMS.md`
- **Integration Help:** See examples in `POSTMAN_COLLECTION.json`
- **Technical Issues:** Check `backend/CLAUDE.md` for development guidelines

---

**You're all set! 🚀**

Start building your insurance application with confidence. All the workflows, business logic, and API endpoints are ready to use.

**Happy coding!**
