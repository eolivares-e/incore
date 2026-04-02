"""Common type definitions for the insurance domain.

This module provides type aliases and custom types used across the application.
"""

from decimal import Decimal
from typing import Annotated
from uuid import UUID

from pydantic import Field, condecimal, constr

# ============================================================================
# Identifier Types
# ============================================================================

PolicyholderId = UUID
PolicyId = UUID
QuoteId = UUID
CoverageId = UUID
ClaimId = UUID
InvoiceId = UUID
PaymentId = UUID
UnderwritingReviewId = UUID
UserId = UUID


# ============================================================================
# Money and Currency Types
# ============================================================================

# Monetary amount with 2 decimal places, must be >= 0
MoneyAmount = Annotated[
    Decimal,
    condecimal(max_digits=12, decimal_places=2, ge=Decimal("0")),
    Field(description="Monetary amount in USD with 2 decimal places"),
]

# Premium amount (can be monthly, annual, etc.)
PremiumAmount = Annotated[
    Decimal,
    condecimal(max_digits=10, decimal_places=2, ge=Decimal("0")),
    Field(description="Insurance premium amount"),
]

# Coverage amount (total insured value)
CoverageAmount = Annotated[
    Decimal,
    condecimal(max_digits=12, decimal_places=2, ge=Decimal("0")),
    Field(description="Total coverage/insured amount"),
]

# Deductible amount
DeductibleAmount = Annotated[
    Decimal,
    condecimal(max_digits=10, decimal_places=2, ge=Decimal("0")),
    Field(description="Deductible amount"),
]

# Percentage (0-100 with 2 decimal places)
Percentage = Annotated[
    Decimal,
    condecimal(max_digits=5, decimal_places=2, ge=Decimal("0"), le=Decimal("100")),
    Field(description="Percentage value (0-100)"),
]


# ============================================================================
# String Types with Constraints
# ============================================================================

# Email (validated by Pydantic's EmailStr, but aliased for clarity)
Email = Annotated[
    str,
    constr(strip_whitespace=True, to_lower=True, max_length=255),
    Field(description="Email address"),
]

# Phone number (basic validation, can be enhanced later)
PhoneNumber = Annotated[
    str,
    constr(
        strip_whitespace=True,
        min_length=10,
        max_length=20,
        pattern=r"^[\d\+\-\(\)\s]+$",
    ),
    Field(description="Phone number with country code", examples=["+1-555-123-4567"]),
]

# ZIP/Postal code
ZipCode = Annotated[
    str,
    constr(strip_whitespace=True, min_length=3, max_length=10),
    Field(description="ZIP or postal code"),
]

# Policy number (unique identifier)
PolicyNumber = Annotated[
    str,
    constr(strip_whitespace=True, to_upper=True, min_length=8, max_length=50),
    Field(
        description="Unique policy number",
        examples=["POL-2024-AUTO-00001", "POL-2024-HOME-00042"],
    ),
]

# Quote number
QuoteNumber = Annotated[
    str,
    constr(strip_whitespace=True, to_upper=True, min_length=8, max_length=50),
    Field(
        description="Unique quote number",
        examples=["QTE-2024-AUTO-00001", "QTE-2024-HOME-00042"],
    ),
]

# Invoice number
InvoiceNumber = Annotated[
    str,
    constr(strip_whitespace=True, to_upper=True, min_length=8, max_length=50),
    Field(
        description="Unique invoice number",
        examples=["INV-2024-00001", "INV-2024-00042"],
    ),
]

# Identification document number
IdentificationNumber = Annotated[
    str,
    constr(strip_whitespace=True, min_length=5, max_length=50),
    Field(description="Identification document number"),
]


# ============================================================================
# Numeric Types
# ============================================================================

# Risk score (0-100)
RiskScore = Annotated[
    int,
    Field(ge=0, le=100, description="Risk assessment score (0=lowest, 100=highest)"),
]

# Age in years
AgeYears = Annotated[
    int,
    Field(ge=0, le=150, description="Age in years"),
]

# Positive integer
PositiveInt = Annotated[
    int,
    Field(gt=0, description="Positive integer value"),
]
