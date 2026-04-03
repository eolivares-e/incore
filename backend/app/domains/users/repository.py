"""Repository for User domain data access."""

from typing import Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domains.users.models import User, UserRole


class UserRepository:
    """Repository for User data access operations."""

    def __init__(self, session: AsyncSession):
        """Initialize repository with database session.

        Args:
            session: SQLAlchemy async session
        """
        self.session = session

    # ========================================================================
    # CRUD Operations
    # ========================================================================

    async def create(
        self,
        email: str,
        hashed_password: str,
        full_name: str,
        role: UserRole = UserRole.CUSTOMER,
        is_superuser: bool = False,
    ) -> User:
        """Create a new user.

        Args:
            email: User email address
            hashed_password: Hashed password
            full_name: User's full name
            role: User role (default: CUSTOMER)
            is_superuser: Superuser flag (default: False)

        Returns:
            Created User instance
        """
        user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role.value,
            is_superuser=is_superuser,
            is_active=True,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Get user by ID.

        Args:
            user_id: User UUID

        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address.

        Args:
            email: User email address

        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def update(self, user_id: UUID, **updates) -> Optional[User]:
        """Update user fields.

        Args:
            user_id: User UUID
            **updates: Fields to update

        Returns:
            Updated User instance or None if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return None

        for key, value in updates.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)

        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def delete(self, user_id: UUID) -> bool:
        """Soft delete user by setting is_active to False.

        Args:
            user_id: User UUID

        Returns:
            True if user was deactivated, False if not found
        """
        user = await self.get_by_id(user_id)
        if not user:
            return False

        user.is_active = False
        await self.session.commit()
        return True

    # ========================================================================
    # Authentication Methods
    # ========================================================================

    async def get_for_login(self, email: str) -> Optional[User]:
        """Get user by email for login (includes hashed_password).

        This is the same as get_by_email but explicitly named for
        authentication purposes.

        Args:
            email: User email address

        Returns:
            User instance with hashed_password or None if not found
        """
        return await self.get_by_email(email)

    async def email_exists(self, email: str) -> bool:
        """Check if email already exists.

        Args:
            email: Email address to check

        Returns:
            True if email exists, False otherwise
        """
        result = await self.session.execute(
            select(func.count()).select_from(User).where(User.email == email)
        )
        count = result.scalar()
        return count > 0

    # ========================================================================
    # User Management Methods
    # ========================================================================

    async def activate_user(self, user_id: UUID) -> Optional[User]:
        """Activate a user account.

        Args:
            user_id: User UUID

        Returns:
            Updated User instance or None if not found
        """
        return await self.update(user_id, is_active=True)

    async def deactivate_user(self, user_id: UUID) -> Optional[User]:
        """Deactivate a user account.

        Args:
            user_id: User UUID

        Returns:
            Updated User instance or None if not found
        """
        return await self.update(user_id, is_active=False)

    async def change_role(self, user_id: UUID, new_role: UserRole) -> Optional[User]:
        """Change user role.

        Args:
            user_id: User UUID
            new_role: New role to assign

        Returns:
            Updated User instance or None if not found
        """
        return await self.update(user_id, role=new_role.value)

    # ========================================================================
    # Query Methods
    # ========================================================================

    async def get_by_role(self, role: UserRole) -> list[User]:
        """Get all users with a specific role.

        Args:
            role: User role to filter by

        Returns:
            List of User instances
        """
        result = await self.session.execute(select(User).where(User.role == role.value))
        return list(result.scalars().all())

    async def filter_users(
        self,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        page: int = 1,
        size: int = 50,
    ) -> tuple[list[User], int]:
        """Filter users with pagination.

        Args:
            role: Optional role filter
            is_active: Optional active status filter
            page: Page number (1-indexed)
            size: Page size

        Returns:
            Tuple of (users list, total count)
        """
        query = select(User)

        # Apply filters
        if role is not None:
            query = query.where(User.role == role.value)
        if is_active is not None:
            query = query.where(User.is_active == is_active)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.session.execute(count_query)
        total = total_result.scalar()

        # Apply pagination
        offset = (page - 1) * size
        query = query.offset(offset).limit(size).order_by(User.created_at.desc())

        # Execute query
        result = await self.session.execute(query)
        users = list(result.scalars().all())

        return users, total
