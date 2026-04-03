"""
Shared FastAPI dependencies for the application.
"""

from uuid import UUID

from app.core.exceptions import AuthorizationException
from app.domains.users.models import User, UserRole


async def validate_policyholder_access(
    policyholder_id: UUID,
    current_user: User,
) -> None:
    """
    Validate that a user can access a specific policyholder.

    For CUSTOMER role: Can only access their own policyholder record.
    For AGENT/UNDERWRITER/ADMIN: Can access any policyholder.

    Note: Currently assumes policyholder_id matches user_id for CUSTOMER role.
    In a real system, you'd fetch the user's associated policyholder_id.

    Args:
        policyholder_id: The policyholder ID being accessed
        current_user: The authenticated user making the request

    Raises:
        AuthorizationException: If user doesn't have access
    """
    if current_user.is_superuser:
        return  # Superusers bypass all checks

    if current_user.role == UserRole.CUSTOMER:
        # For CUSTOMER role, they can only access their own data
        # TODO: Add policyholder_id foreign key to User model
        # For now, we'll use a simplified check
        # In production, you'd query: user.policyholder_id == policyholder_id
        if str(current_user.id) != str(policyholder_id):
            raise AuthorizationException(
                "You can only access your own policyholder information"
            )


async def validate_policy_access(
    policy_id: UUID,
    current_user: User,
) -> None:
    """
    Validate that a user can access a specific policy.

    For CUSTOMER role: Can only access policies linked to their policyholder.
    For AGENT/UNDERWRITER/ADMIN: Can access any policy.

    Args:
        policy_id: The policy ID being accessed
        current_user: The authenticated user making the request

    Raises:
        AuthorizationException: If user doesn't have access
    """
    if current_user.is_superuser:
        return

    if current_user.role == UserRole.CUSTOMER:
        # TODO: Query policy.policyholder_id and compare with user's policyholder_id
        # For now, simplified check - in production you'd need DB query
        raise AuthorizationException("You can only access your own policies")


async def validate_quote_access(
    quote_id: UUID,
    current_user: User,
) -> None:
    """
    Validate that a user can access a specific quote.

    For CUSTOMER role: Can only access quotes linked to their policyholder.
    For AGENT/UNDERWRITER/ADMIN: Can access any quote.

    Args:
        quote_id: The quote ID being accessed
        current_user: The authenticated user making the request

    Raises:
        AuthorizationException: If user doesn't have access
    """
    if current_user.is_superuser:
        return

    if current_user.role == UserRole.CUSTOMER:
        # TODO: Query quote.policyholder_id and compare with user's policyholder_id
        raise AuthorizationException("You can only access your own quotes")


async def validate_invoice_access(
    invoice_id: UUID,
    current_user: User,
) -> None:
    """
    Validate that a user can access a specific invoice.

    For CUSTOMER role: Can only access invoices for their policies.
    For AGENT/ADMIN: Can access any invoice.

    Args:
        invoice_id: The invoice ID being accessed
        current_user: The authenticated user making the request

    Raises:
        AuthorizationException: If user doesn't have access
    """
    if current_user.is_superuser:
        return

    if current_user.role == UserRole.CUSTOMER:
        # TODO: Query invoice.policy.policyholder_id and compare
        raise AuthorizationException("You can only access your own invoices")
