"""Service layer for User authentication and authorization."""

from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ValidationException,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_password_hash,
    validate_password_strength,
    verify_password,
    verify_token,
)
from app.domains.users.models import User, UserRole
from app.domains.users.repository import UserRepository


class AuthService:
    """Service for authentication and authorization operations."""

    def __init__(self, session: AsyncSession):
        """Initialize service with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session
        self.repository = UserRepository(session)

    # ========================================================================
    # User Registration
    # ========================================================================

    async def register_user(self, email: str, password: str, full_name: str) -> User:
        """Register a new user (self-registration).

        Creates a new user account with CUSTOMER role.

        Args:
            email: User email address
            password: Plain text password
            full_name: User's full name

        Returns:
            Created User instance

        Raises:
            ValidationException: If email already exists or password is weak
        """
        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            raise ValidationException(error_msg)

        # Check if email already exists
        if await self.repository.email_exists(email):
            raise ValidationException(f"Email {email} is already registered")

        # Hash password
        hashed_password = get_password_hash(password)

        # Create user with CUSTOMER role
        user = await self.repository.create(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=UserRole.CUSTOMER,
            is_superuser=False,
        )

        return user

    # ========================================================================
    # User Login
    # ========================================================================

    async def login_user(self, email: str, password: str) -> tuple[User, str, str]:
        """Authenticate user and create tokens.

        Args:
            email: User email address
            password: Plain text password

        Returns:
            Tuple of (User, access_token, refresh_token)

        Raises:
            AuthenticationException: If credentials are invalid or user is inactive
        """
        # Find user by email
        user = await self.repository.get_for_login(email)
        if not user:
            raise AuthenticationException("Invalid email or password")

        # Verify password
        if not verify_password(password, user.hashed_password):
            raise AuthenticationException("Invalid email or password")

        # Check if user is active
        if not user.is_active:
            raise AuthenticationException(
                "Account is inactive. Please contact support."
            )

        # Create tokens
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))

        return user, access_token, refresh_token

    # ========================================================================
    # Token Management
    # ========================================================================

    async def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token.

        No token rotation - returns same refresh token for simplicity.

        Args:
            refresh_token: JWT refresh token

        Returns:
            New access token

        Raises:
            AuthenticationException: If refresh token is invalid
        """
        # Verify refresh token
        user_id_str = verify_token(refresh_token)
        if not user_id_str:
            raise AuthenticationException("Invalid or expired refresh token")

        # Parse user ID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise AuthenticationException("Invalid token format")

        # Get user and verify they're still active
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise AuthenticationException("User not found")

        if not user.is_active:
            raise AuthenticationException("Account is inactive")

        # Create new access token
        access_token = create_access_token(subject=str(user.id))

        return access_token

    async def get_current_user(self, token: str) -> User:
        """Get current authenticated user from access token.

        Args:
            token: JWT access token

        Returns:
            User instance

        Raises:
            AuthenticationException: If token is invalid or user not found
        """
        # Verify token
        user_id_str = verify_token(token)
        if not user_id_str:
            raise AuthenticationException("Invalid or expired token")

        # Parse user ID
        try:
            user_id = UUID(user_id_str)
        except ValueError:
            raise AuthenticationException("Invalid token format")

        # Get user
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise AuthenticationException("User not found")

        if not user.is_active:
            raise AuthenticationException("Account is inactive")

        return user

    # ========================================================================
    # Authorization
    # ========================================================================

    async def validate_user_for_action(
        self, user: User, required_roles: list[UserRole]
    ) -> bool:
        """Validate if user has permission for action.

        Superusers bypass all role checks.

        Args:
            user: User instance
            required_roles: List of roles allowed to perform action

        Returns:
            True if user has permission

        Raises:
            AuthorizationException: If user lacks permission
        """
        # Superusers can do anything
        if user.is_superuser:
            return True

        # Check if user's role is in required roles
        user_role = UserRole(user.role)
        if user_role not in required_roles:
            raise AuthorizationException(
                f"Action requires one of roles: {[r.value for r in required_roles]}"
            )

        return True

    # ========================================================================
    # User Management (Admin)
    # ========================================================================

    async def create_user(
        self,
        email: str,
        password: str,
        full_name: str,
        role: UserRole = UserRole.CUSTOMER,
        is_superuser: bool = False,
    ) -> User:
        """Create a new user (admin operation).

        Args:
            email: User email address
            password: Plain text password
            full_name: User's full name
            role: User role
            is_superuser: Superuser flag

        Returns:
            Created User instance

        Raises:
            ValidationException: If email already exists or password is weak
        """
        # Validate password strength
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            raise ValidationException(error_msg)

        # Check if email already exists
        if await self.repository.email_exists(email):
            raise ValidationException(f"Email {email} is already registered")

        # Hash password
        hashed_password = get_password_hash(password)

        # Create user
        user = await self.repository.create(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role,
            is_superuser=is_superuser,
        )

        return user

    async def update_user_profile(
        self,
        user_id: UUID,
        full_name: Optional[str] = None,
        password: Optional[str] = None,
    ) -> User:
        """Update user profile.

        Args:
            user_id: User UUID
            full_name: New full name (optional)
            password: New password (optional)

        Returns:
            Updated User instance

        Raises:
            ValidationException: If user not found or password is weak
        """
        user = await self.repository.get_by_id(user_id)
        if not user:
            raise ValidationException("User not found")

        updates = {}

        if full_name is not None:
            updates["full_name"] = full_name

        if password is not None:
            # Validate password strength
            is_valid, error_msg = validate_password_strength(password)
            if not is_valid:
                raise ValidationException(error_msg)
            updates["hashed_password"] = get_password_hash(password)

        if updates:
            user = await self.repository.update(user_id, **updates)

        return user

    async def change_user_role(
        self, admin_user: User, target_user_id: UUID, new_role: UserRole
    ) -> User:
        """Change user role (admin only).

        Args:
            admin_user: Admin user performing action
            target_user_id: Target user UUID
            new_role: New role to assign

        Returns:
            Updated User instance

        Raises:
            AuthorizationException: If admin lacks permission
            ValidationException: If target user not found
        """
        # Validate admin has permission
        await self.validate_user_for_action(admin_user, [UserRole.ADMIN])

        # Get target user
        target_user = await self.repository.get_by_id(target_user_id)
        if not target_user:
            raise ValidationException("Target user not found")

        # Change role
        updated_user = await self.repository.change_role(target_user_id, new_role)

        return updated_user

    async def activate_user(self, admin_user: User, target_user_id: UUID) -> User:
        """Activate user account (admin only).

        Args:
            admin_user: Admin user performing action
            target_user_id: Target user UUID

        Returns:
            Updated User instance

        Raises:
            AuthorizationException: If admin lacks permission
            ValidationException: If target user not found
        """
        # Validate admin has permission
        await self.validate_user_for_action(admin_user, [UserRole.ADMIN])

        # Activate user
        user = await self.repository.activate_user(target_user_id)
        if not user:
            raise ValidationException("User not found")

        return user

    async def deactivate_user(self, admin_user: User, target_user_id: UUID) -> User:
        """Deactivate user account (admin only).

        Args:
            admin_user: Admin user performing action
            target_user_id: Target user UUID

        Returns:
            Updated User instance

        Raises:
            AuthorizationException: If admin lacks permission
            ValidationException: If target user not found
        """
        # Validate admin has permission
        await self.validate_user_for_action(admin_user, [UserRole.ADMIN])

        # Deactivate user
        user = await self.repository.deactivate_user(target_user_id)
        if not user:
            raise ValidationException("User not found")

        return user

    async def list_users(
        self,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 50,
    ) -> tuple[list[User], int]:
        """List users with filters and pagination.

        Args:
            role: Optional role filter
            is_active: Optional active status filter
            page: Page number (1-indexed)
            size: Page size

        Returns:
            Tuple of (users list, total count)
        """
        return await self.repository.filter_users(
            role=role, is_active=is_active, page=page, size=size
        )
