"""CLI command to create initial admin user."""

import asyncio
import sys

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import get_password_hash
from app.domains.users.models import UserRole
from app.domains.users.repository import UserRepository


async def create_admin():
    """Create initial admin user via CLI command.

    Usage:
        python -m app.domains.users.cli create-admin

    Creates admin user with:
    - Email: admin@insurance-core.local
    - Password: admin
    - Role: ADMIN
    - is_superuser: True
    """
    # Create async engine
    engine = create_async_engine(settings.DATABASE_URL, echo=False)

    # Create async session
    async_session_maker = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with async_session_maker() as session:
        repository = UserRepository(session)

        # Check if admin already exists
        admin_email = "admin@insurance-core.local"
        existing_admin = await repository.get_by_email(admin_email)

        if existing_admin:
            print(f"✗ Admin user '{admin_email}' already exists.")
            print(f"  User ID: {existing_admin.id}")
            print(f"  Created: {existing_admin.created_at}")
            return

        # Create admin user
        admin_password = "admin"
        hashed_password = get_password_hash(admin_password)

        admin_user = await repository.create(
            email=admin_email,
            hashed_password=hashed_password,
            full_name="System Administrator",
            role=UserRole.ADMIN,
            is_superuser=True,
        )

        print("✓ Admin user created successfully!")
        print(f"  Email: {admin_user.email}")
        print(f"  Password: {admin_password}")
        print(f"  User ID: {admin_user.id}")
        print(f"  Role: {admin_user.role}")
        print(f"  Superuser: {admin_user.is_superuser}")
        print()
        print("⚠️  WARNING: Change the default password for security!")

    await engine.dispose()


def main():
    """Main entry point for CLI."""
    if len(sys.argv) < 2:
        print("Usage: python -m app.domains.users.cli <command>")
        print("Commands:")
        print("  create-admin  - Create initial admin user")
        sys.exit(1)

    command = sys.argv[1]

    if command == "create-admin":
        asyncio.run(create_admin())
    else:
        print(f"Unknown command: {command}")
        print("Available commands: create-admin")
        sys.exit(1)


if __name__ == "__main__":
    main()
