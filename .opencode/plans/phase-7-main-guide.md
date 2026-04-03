# Phase 7: Authentication & Authorization Implementation Guide

**Status**: Ready for Implementation  
**Branch**: `feature/phase-7-auth`  
**PR**: #9 (to be created)  
**Dependencies**: Phase 0 (already has security utils)  
**Last Updated**: 2026-04-03

---

## Overview

Implement JWT-based authentication and role-based access control (RBAC). Foundation is already in place in `core/security.py` with token/password utilities.

---

## Design Decisions

✅ **User Roles**: ADMIN, UNDERWRITER, AGENT, CUSTOMER (defined in users/models.py)  
✅ **Token Strategy**: JWT with access + refresh tokens (no rotation - same refresh token for 7 days)  
✅ **Password Policy**: Min 8 chars, 1 digit, 1 uppercase, 1 lowercase (already in code)  
✅ **Protected Endpoints**: Phase 8 only - Phase 7 creates auth infrastructure  
✅ **User Identification**: Email-based login, UUID internal ID  
✅ **Superuser Flag**: For admins to bypass some role restrictions  
✅ **Admin Creation**: Via CLI command `python -m app.domains.users.cli create-admin`  
✅ **Admin Credentials**: admin@insurance-core.local / admin (hardcoded for dev)  
✅ **Token Transmission**: Authorization: Bearer <token> header  
✅ **Router Structure**: Two separate routers (auth_router + users_router)  

---

## Implementation Checklist

### Setup Phase
```bash
git checkout -b feature/phase-7-auth
mkdir -p backend/app/domains/users
```

### Core Implementation (7 Files)

#### 1. User Model
**File**: `backend/app/domains/users/models.py` (~150 lines)

Key Components:
- User model: id, email, hashed_password, full_name, is_active, is_superuser, role
- UserRole enum: ADMIN, UNDERWRITER, AGENT, CUSTOMER
- Relationships: None initially (can add to policies/claims later)
- Properties: is_admin, is_active_and_enabled

**Check Constraints**:
- Email format validation
- Password not stored in plaintext

#### 2. Schemas
**File**: `backend/app/domains/users/schemas.py` (~200 lines)

Schemas:
- UserCreate (email, password, full_name)
- UserUpdate (full_name, password optional)
- UserResponse (public view: id, email, full_name, role)
- UserRegisterRequest (email, password, full_name)
- UserLoginRequest (email, password)
- TokenResponse (access_token, refresh_token, token_type)
- TokenRefreshRequest (refresh_token)
- CurrentUserResponse (includes role, is_superuser)

**Validators**:
- Email format and uniqueness check (deferred to service)
- Password strength (use existing validate_password_strength)
- Full name: non-empty, max 100 chars

#### 3. Repository
**File**: `backend/app/domains/users/repository.py` (~200 lines)

UserRepository:
- create(email, hashed_password, full_name, role)
- get_by_id(user_id)
- get_by_email(email)
- update(user_id, updates)
- delete(user_id)
- get_by_role(role) - for admin dashboards
- filter_users(role, is_active, pagination)

**Special Methods**:
- get_for_login(email) - returns with hashed_password
- email_exists(email) - for validation
- activate_user(user_id)
- deactivate_user(user_id)

#### 4. Service
**File**: `backend/app/domains/users/service.py` (~300 lines)

AuthService:
- register_user(email, password, full_name) → User
  - Validate password strength
  - Check email not taken
  - Hash password
  - Create user (default role: CUSTOMER)
- login_user(email, password) → (User, access_token, refresh_token)
  - Find user by email
  - Verify password
  - Create tokens
- refresh_access_token(refresh_token) → access_token
  - Verify refresh token is valid and type="refresh"
  - Create new access token
  - Return SAME refresh token (no rotation for simplicity)
- get_current_user(token: str) → User
  - Verify access token
  - Get user by ID from token
  - Check user is active
- validate_user_for_action(user, required_roles: list) → bool
  - Check user is superuser OR has required role

#### 5. Router
**File**: `backend/app/domains/users/router.py` (~280 lines)

**Two Routers**:

**auth_router** (prefix: `/auth`, 6 endpoints):
1. `POST /auth/register` - Register new user (public)
2. `POST /auth/login` - Login (returns tokens) (public)
3. `POST /auth/refresh` - Refresh access token (public)
4. `GET /auth/me` - Get current user info (protected)
5. `PUT /auth/me` - Update current user (protected)
6. `POST /auth/logout` - Logout (protected, optional)

**users_router** (prefix: `/users`, 5 endpoints - all require ADMIN role):
7. `GET /users` - List all users (with filters)
8. `GET /users/{id}` - Get user by ID
9. `PUT /users/{id}/role` - Change user role
10. `PUT /users/{id}/activate` - Activate user
11. `PUT /users/{id}/deactivate` - Deactivate user

**Auth Dependencies**:
```python
def get_current_user(token: str = Depends(HTTPBearer())) -> User:
    user = await auth_service.get_current_user(token.credentials)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user

def require_role(*roles: UserRole):
    async def role_checker(user: User = Depends(get_current_user)):
        if user.is_superuser:
            return user
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return role_checker
```

#### 6. Init File
**File**: `backend/app/domains/users/__init__.py` (~20 lines)

```python
"""Users and authentication domain."""

from app.domains.users.models import User, UserRole
from app.domains.users.router import auth_router, users_router
from app.domains.users.schemas import (
    UserCreate,
    UserResponse,
    TokenResponse,
    CurrentUserResponse,
)
from app.domains.users.service import AuthService

__all__ = [
    "User",
    "UserRole",
    "auth_router",
    "users_router",
    "UserCreate",
    "UserResponse",
    "TokenResponse",
    "CurrentUserResponse",
    "AuthService",
]
```

#### 7. CLI Command
**File**: `backend/app/domains/users/cli.py` (~120 lines)

**Command**: `python -m app.domains.users.cli create-admin`

Creates initial admin user:
- Email: admin@insurance-core.local
- Password: "admin" (hardcoded for development)
- Full Name: "System Administrator"
- Role: UserRole.ADMIN
- is_superuser: True
- is_active: True

**Behavior**:
- Check if admin@insurance-core.local already exists
- If exists: Print "Admin already exists" and exit
- If not: Create admin user
- Print success message with credentials

### Database Migration

#### 8. Create Migration
```bash
cd backend
alembic revision --autogenerate -m "add users table"
```

**Tables**:
- `users` (8 columns: id, email, hashed_password, full_name, role, is_active, is_superuser, created_at, updated_at)

**Indexes**:
1. users.email (unique)
2. users.role
3. users.is_active
4. Composite: (is_active, role)

**Check Constraints**:
- email format (basic regex or allow DB-level validation)

Apply:
```bash
alembic upgrade head
```

### Integration

#### 9. Update Config
**File**: `backend/app/core/config.py`

Optional additions:
- `INITIAL_ADMIN_EMAIL: str = "admin@insurance-core.local"`

#### 10. Register Routers
**File**: `backend/app/main.py`

Add both routers:
```python
from app.domains.users.router import auth_router, users_router

app.include_router(auth_router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(users_router, prefix=settings.API_V1_STR, tags=["users"])
```

**Note**: Endpoint protection (adding auth dependencies to existing routers) is deferred to Phase 8.

### Testing

#### 11. Create Test Suite
**File**: `backend/tests/test_users.py` (~400 lines, 30 tests)

Test Categories:
- Model tests (4): repr, properties, relationships
- Schema tests (8): validation, email format, password strength
- Repository tests (6): CRUD, get_by_email, email_exists
- Service tests (8): register, login, token refresh, role validation
- Router tests (4): register endpoint, login endpoint, protected endpoint, invalid token

**Mock/Fixture Strategy**:
- No external dependencies to mock
- Use test database fixtures
- Create sample users with different roles

Example Tests:
```python
async def test_register_user_success(db)
async def test_register_duplicate_email(db)
async def test_login_success(db)
async def test_login_wrong_password(db)
async def test_refresh_token(db)
async def test_get_current_user_valid_token(db)
async def test_get_current_user_invalid_token(db)
async def test_require_role_sufficient_permissions(db)
async def test_require_role_insufficient_permissions(db)
```

Run:
```bash
pytest tests/test_users.py -v
pytest tests/ -v  # All tests (expect ~210 total)
```

### Code Quality & Documentation

#### 12. Verify PEP 8
```bash
ruff check backend/
```

#### 13. Update Implementation Plan
**File**: `docs/IMPLEMENTATION_PLAN.md`

Update:
- Current Phase: Phase 7 (Complete)
- Progress: 7/9 (78%)
- Phase 7 section with completion details

### Git Workflow

#### 14. Commit & Push
```bash
git add .
git commit -m "feat: implement Phase 7 - Authentication & Authorization"
git push -u origin feature/phase-7-auth
```

#### 15. Create PR #9

---

## Scope Summary

**Files to Create**: 8 files (~1,700 lines)
- models.py: ~170 lines
- schemas.py: ~200 lines
- repository.py: ~200 lines
- service.py: ~300 lines
- router.py: ~280 lines (two routers)
- cli.py: ~120 lines
- __init__.py: ~20 lines
- test_users.py: ~400 lines (30 tests)

**Files to Modify**: 2 files
- core/config.py: ~2 lines (optional INITIAL_ADMIN_EMAIL)
- main.py: ~8 lines (register both routers)
- IMPLEMENTATION_PLAN.md: ~40 lines

**Migration**: 1 (1 table, 4 indexes, 1 constraint)

**Total**: ~1,700 new lines

---

## Key Considerations

1. **Circular Dependencies**: User model in domains might conflict with existing imports. Use TYPE_CHECKING for forward refs.

2. **Token Expiration**: Access tokens: 30 min (default), Refresh tokens: 7 days (default)

3. **Password Hashing**: Uses bcrypt (already in code via passlib)

4. **Role Propagation**: When creating quotes/policies, should track which user created them (user_id FK)

5. **Backward Compatibility**: Existing endpoints work without auth for now. Protect in Phase 8 cross-domain integration.

6. **Admin Creation**: CLI command `python -m app.domains.users.cli create-admin` (credentials: admin@insurance-core.local / admin)

---

## Next Phase (Phase 8)

After Phase 7 is complete:
- Protect all endpoints with `Depends(get_current_user)`
- Add role checks: UNDERWRITER for underwriting endpoints, AGENT for policy creation, etc.
- Add user_id tracking to policies, quotes, underwriting_reviews tables
- Phase 8 does integration and polishing
