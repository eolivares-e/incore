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

✅ **User Roles**: ADMIN, UNDERWRITER, AGENT, CUSTOMER  
✅ **Token Strategy**: JWT with access + refresh tokens  
✅ **Password Policy**: Min 8 chars, 1 digit, 1 uppercase, 1 lowercase (already in code)  
✅ **Protected Endpoints**: All domain endpoints except auth/public  
✅ **User Identification**: Email-based login, UUID internal ID  
✅ **Superuser Flag**: For admins to bypass some role restrictions  

---

## Implementation Checklist

### Setup Phase
```bash
git checkout -b feature/phase-7-auth
mkdir -p backend/app/domains/users
```

### Core Implementation (5 Files)

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
  - Verify refresh token is valid
  - Create new access token
  - Optional: return new refresh token
- get_current_user(token: str) → User
  - Verify access token
  - Get user by ID from token
  - Check user is active
- validate_user_for_action(user, required_roles: list) → bool
  - Check user is superuser OR has required role

#### 5. Router
**File**: `backend/app/domains/users/router.py` (~250 lines)

Public Endpoints (no auth required):
1. `POST /auth/register` - Register new user
2. `POST /auth/login` - Login (returns tokens)
3. `POST /auth/refresh` - Refresh access token

Protected Endpoints (require valid JWT):
4. `GET /auth/me` - Get current user info
5. `PUT /auth/me` - Update current user (password, full_name)
6. `POST /auth/logout` - Logout (client-side token deletion, optional)

Admin Endpoints (require ADMIN role):
7. `GET /users` - List all users (with role filter)
8. `GET /users/{id}` - Get user by ID
9. `PUT /users/{id}/role` - Change user role (ADMIN only)
10. `PUT /users/{id}/activate` - Activate user (ADMIN only)
11. `PUT /users/{id}/deactivate` - Deactivate user (ADMIN only)

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
from app.domains.users.router import router
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
    "router",
    "UserCreate",
    "UserResponse",
    "TokenResponse",
    "CurrentUserService",
    "AuthService",
]
```

### Database Migration

#### 7. Create Migration
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

#### 8. Update Config
**File**: `backend/app/core/config.py`

Optional additions:
- `INITIAL_ADMIN_EMAIL: str = "admin@insurance-core.local"`
- `INITIAL_ADMIN_PASSWORD: str = ""`
- `ENABLE_ADMIN_CREATION: bool = True`

#### 9. Register Router & Dependencies
**File**: `backend/app/main.py`

Add:
```python
from app.domains.users.router import router as users_router
from app.domains.users.dependencies import get_current_user

app.include_router(users_router, prefix=settings.API_V1_STR, tags=["auth"])
```

#### 10. Protect Existing Domain Endpoints
Update all existing routers (policies, pricing, underwriting, billing):
- Add `Depends(get_current_user)` to endpoints that should be protected
- Consider role-based access (e.g., only UNDERWRITER can approve reviews)
- Leave public endpoints open (e.g., GET /health)

Examples:
```python
@router.post("/policies", dependencies=[Depends(require_role(UserRole.ADMIN, UserRole.AGENT))])
async def create_policy(...)

@router.post("/underwriting/reviews/{id}/approve", dependencies=[Depends(require_role(UserRole.UNDERWRITER))])
async def approve_review(...)
```

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

**Files to Create**: 6 files (~1,120 lines)
- models.py: ~150 lines
- schemas.py: ~200 lines
- repository.py: ~200 lines
- service.py: ~300 lines
- router.py: ~250 lines
- __init__.py: ~20 lines

**Files to Modify**: 4 files
- core/config.py: ~3 lines (optional)
- main.py: ~5 lines
- All 5 domain routers: Add auth dependencies (~1-3 lines each)
- IMPLEMENTATION_PLAN.md: ~40 lines

**Tests**: 1 file (~400 lines, 30 tests)

**Migration**: 1 (1 table, 4 indexes, 1 constraint)

**Total**: ~1,520 new lines

---

## Key Considerations

1. **Circular Dependencies**: User model in domains might conflict with existing imports. Use TYPE_CHECKING for forward refs.

2. **Token Expiration**: Access tokens: 30 min (default), Refresh tokens: 7 days (default)

3. **Password Hashing**: Uses bcrypt (already in code via passlib)

4. **Role Propagation**: When creating quotes/policies, should track which user created them (user_id FK)

5. **Backward Compatibility**: Existing endpoints work without auth for now. Protect in Phase 8 cross-domain integration.

6. **Admin Creation**: Consider seed script to create initial ADMIN user

---

## Next Phase (Phase 8)

After Phase 7 is complete:
- Protect all endpoints with `Depends(get_current_user)`
- Add role checks: UNDERWRITER for underwriting endpoints, AGENT for policy creation, etc.
- Add user_id tracking to policies, quotes, underwriting_reviews tables
- Phase 8 does integration and polishing
