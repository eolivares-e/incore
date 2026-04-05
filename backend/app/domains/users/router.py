"""API routers for authentication and user management."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ValidationException,
)
from app.domains.users.models import User, UserRole
from app.domains.users.schemas import (
    AdminUserCreate,
    AdminUserUpdate,
    CurrentUserResponse,
    TokenRefreshRequest,
    TokenResponse,
    UserListResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserRoleUpdate,
    UserUpdate,
)
from app.domains.users.service import AuthService

# ============================================================================
# Routers
# ============================================================================

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])
users_router = APIRouter(prefix="/users", tags=["User Management"])

# Security scheme
security = HTTPBearer()


# ============================================================================
# Dependencies
# ============================================================================


async def get_auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    """Dependency to get AuthService instance."""
    return AuthService(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Dependency to get current authenticated user from token.

    Args:
        credentials: HTTP Bearer token
        auth_service: Auth service instance

    Returns:
        Authenticated User instance

    Raises:
        HTTPException: 401 if token is invalid or user is inactive
    """
    try:
        user = await auth_service.get_current_user(credentials.credentials)
        return user
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


def require_role(*roles: UserRole):
    """Dependency factory to require specific roles.

    Superusers bypass role checks.

    Args:
        *roles: Required roles

    Returns:
        Dependency function that validates user role

    Raises:
        HTTPException: 403 if user lacks required role
    """

    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        """Check if user has required role."""
        if current_user.is_superuser:
            return current_user

        user_role = UserRole(current_user.role)
        if user_role not in roles:
            required = [r.value for r in roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {required}",
            )

        return current_user

    return role_checker


# ============================================================================
# Authentication Endpoints (Public + Protected)
# ============================================================================


@auth_router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description=(
        "Self-registration endpoint for new users. Creates account with CUSTOMER role."
    ),
)
async def register(
    data: UserRegisterRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Register a new user account.

    **Public endpoint - no authentication required**

    Creates a new user with CUSTOMER role. Email must be unique.

    Returns:
    - 201: User created successfully
    - 400: Validation error (duplicate email, weak password)
    """
    try:
        user = await auth_service.register_user(
            email=data.email, password=data.password, full_name=data.full_name
        )
        return UserResponse.model_validate(user)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and receive JWT tokens.",
)
async def login(
    data: UserLoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Login and receive JWT tokens.

    **Public endpoint - no authentication required**

    Returns access token (30min) and refresh token (7 days).

    Returns:
    - 200: Login successful, returns tokens
    - 401: Invalid credentials or inactive account
    """
    try:
        user, access_token, refresh_token = await auth_service.login_user(
            email=data.email, password=data.password
        )
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="Bearer",
        )
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@auth_router.post(
    "/refresh",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Get new access token using refresh token.",
)
async def refresh_token(
    data: TokenRefreshRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Refresh access token.

    **Public endpoint - no authentication required**

    Provide refresh token to get new access token.
    Refresh token is NOT rotated (same token remains valid).

    Returns:
    - 200: New access token
    - 401: Invalid or expired refresh token
    """
    try:
        access_token = await auth_service.refresh_access_token(data.refresh_token)
        return {
            "access_token": access_token,
            "token_type": "Bearer",
        }
    except AuthenticationException as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@auth_router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user",
    description="Get current authenticated user information.",
)
async def get_me(
    current_user: User = Depends(get_current_user),
) -> CurrentUserResponse:
    """Get current authenticated user.

    **Protected endpoint - requires valid access token**

    Returns full user information including role and superuser status.

    Returns:
    - 200: User information
    - 401: Invalid or expired token
    """
    return CurrentUserResponse.model_validate(current_user)


@auth_router.put(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user",
    description="Update current user's profile (full name, password).",
)
async def update_me(
    data: UserUpdate,
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Update current user profile.

    **Protected endpoint - requires valid access token**

    Can update full name and/or password.

    Returns:
    - 200: User updated successfully
    - 400: Validation error (weak password)
    - 401: Invalid or expired token
    """
    try:
        updated_user = await auth_service.update_user_profile(
            user_id=current_user.id,
            full_name=data.full_name,
            password=data.password,
        )
        return UserResponse.model_validate(updated_user)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@auth_router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Logout user",
    description="Logout endpoint (client-side token deletion).",
)
async def logout(
    current_user: User = Depends(get_current_user),
) -> None:
    """Logout user.

    **Protected endpoint - requires valid access token**

    This is a no-op endpoint. Client should delete tokens locally.
    JWT tokens cannot be invalidated server-side without a token blacklist.

    Returns:
    - 204: Logout acknowledged
    - 401: Invalid or expired token
    """
    # No server-side action needed
    # Client should delete tokens from storage
    return None


# ============================================================================
# User Management Endpoints (Admin Only)
# ============================================================================


@users_router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    summary="List users",
    description="List all users with filters and pagination (admin only).",
)
async def list_users(
    role: UserRole | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    page: int = 1,
    size: int = 50,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserListResponse:
    """List users with filters.

    **Admin only endpoint**

    Supports filtering by role, active status, and name/email search, with pagination.

    Returns:
    - 200: User list
    - 401: Invalid or expired token
    - 403: Insufficient permissions
    """
    users, total = await auth_service.list_users(
        role=role, is_active=is_active, search=search, page=page, size=size
    )

    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        size=size,
    )


@users_router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID",
    description="Get user details by ID (admin only).",
)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Get user by ID.

    **Admin only endpoint**

    Returns:
    - 200: User details
    - 401: Invalid or expired token
    - 403: Insufficient permissions
    - 404: User not found
    """
    user = await auth_service.repository.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return UserResponse.model_validate(user)


@users_router.put(
    "/{user_id}/role",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Change user role",
    description="Change user role (admin only).",
)
async def change_user_role(
    user_id: UUID,
    data: UserRoleUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Change user role.

    **Admin only endpoint**

    Returns:
    - 200: User role updated
    - 400: Validation error
    - 401: Invalid or expired token
    - 403: Insufficient permissions
    - 404: User not found
    """
    try:
        updated_user = await auth_service.change_user_role(
            admin_user=current_user, target_user_id=user_id, new_role=data.role
        )
        return UserResponse.model_validate(updated_user)
    except (ValidationException, AuthorizationException) as e:
        status_code = (
            status.HTTP_400_BAD_REQUEST
            if isinstance(e, ValidationException)
            else status.HTTP_403_FORBIDDEN
        )
        raise HTTPException(status_code=status_code, detail=str(e))


@users_router.put(
    "/{user_id}/activate",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Activate user",
    description="Activate user account (admin only).",
)
async def activate_user(
    user_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Activate user account.

    **Admin only endpoint**

    Returns:
    - 200: User activated
    - 400: Validation error
    - 401: Invalid or expired token
    - 403: Insufficient permissions
    - 404: User not found
    """
    try:
        user = await auth_service.activate_user(
            admin_user=current_user, target_user_id=user_id
        )
        return UserResponse.model_validate(user)
    except (ValidationException, AuthorizationException) as e:
        status_code = (
            status.HTTP_400_BAD_REQUEST
            if isinstance(e, ValidationException)
            else status.HTTP_403_FORBIDDEN
        )
        raise HTTPException(status_code=status_code, detail=str(e))


@users_router.put(
    "/{user_id}/deactivate",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate user",
    description="Deactivate user account (admin only).",
)
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Deactivate user account.

    **Admin only endpoint**

    Returns:
    - 200: User deactivated
    - 400: Validation error
    - 401: Invalid or expired token
    - 403: Insufficient permissions
    - 404: User not found
    """
    try:
        user = await auth_service.deactivate_user(
            admin_user=current_user, target_user_id=user_id
        )
        return UserResponse.model_validate(user)
    except (ValidationException, AuthorizationException) as e:
        status_code = (
            status.HTTP_400_BAD_REQUEST
            if isinstance(e, ValidationException)
            else status.HTTP_403_FORBIDDEN
        )
        raise HTTPException(status_code=status_code, detail=str(e))


@users_router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user",
    description="Create a new user with any role (admin only).",
)
async def create_user(
    data: AdminUserCreate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Create a new user.

    **Admin only endpoint**

    Returns:
    - 201: User created
    - 400: Validation error (duplicate email, weak password)
    - 401: Invalid or expired token
    - 403: Insufficient permissions
    """
    try:
        user = await auth_service.admin_create_user(
            email=data.email,
            password=data.password,
            full_name=data.full_name,
            role=data.role,
        )
        return UserResponse.model_validate(user)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@users_router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user",
    description="Update a user's full name or email (admin only).",
)
async def update_user(
    user_id: UUID,
    data: AdminUserUpdate,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> UserResponse:
    """Update user profile.

    **Admin only endpoint**

    Returns:
    - 200: User updated
    - 400: Validation error
    - 401: Invalid or expired token
    - 403: Insufficient permissions
    - 404: User not found
    """
    try:
        user = await auth_service.admin_update_user(
            target_user_id=user_id,
            full_name=data.full_name,
            email=str(data.email) if data.email else None,
        )
        return UserResponse.model_validate(user)
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@users_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user",
    description="Permanently delete a user (admin only). Cannot delete superusers.",
)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(require_role(UserRole.ADMIN)),
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    """Permanently delete a user.

    **Admin only endpoint**

    Returns:
    - 204: User deleted
    - 400: Validation error (user not found)
    - 401: Invalid or expired token
    - 403: Insufficient permissions (or target is superuser)
    """
    try:
        await auth_service.delete_user(
            admin_user=current_user, target_user_id=user_id
        )
    except (ValidationException, AuthorizationException) as e:
        status_code = (
            status.HTTP_400_BAD_REQUEST
            if isinstance(e, ValidationException)
            else status.HTTP_403_FORBIDDEN
        )
        raise HTTPException(status_code=status_code, detail=str(e))
