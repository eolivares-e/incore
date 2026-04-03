"""Tests for the Billing domain."""

from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import uuid4

import pytest

from app.domains.billing.schemas import (
    InvoiceCreate,
    StripePaymentIntentCreate,
)
from app.domains.billing.service import StripeProvider
from app.shared.enums import InvoiceStatus, PaymentMethod, PaymentStatus

# ============================================================================
# Schema Tests
# ============================================================================


class TestBillingSchemas:
    """Tests for billing schemas."""

    def test_invoice_create_schema_validation(self):
        """Test InvoiceCreate schema validation."""
        # Valid data
        valid_data = InvoiceCreate(
            policy_id=uuid4(),
            amount_due=Decimal("100.00"),
            due_date=date.today() + timedelta(days=30),
        )
        assert valid_data.amount_due == Decimal("100.00")

        # Invalid: due_date in past
        with pytest.raises(ValueError, match="due_date cannot be in the past"):
            InvoiceCreate(
                policy_id=uuid4(),
                amount_due=Decimal("100.00"),
                due_date=date.today() - timedelta(days=1),
            )

        # Invalid: negative amount
        with pytest.raises(ValueError):
            InvoiceCreate(
                policy_id=uuid4(),
                amount_due=Decimal("-100.00"),
                due_date=date.today() + timedelta(days=30),
            )

    def test_stripe_payment_intent_create_validation(self):
        """Test StripePaymentIntentCreate schema validation."""
        # Valid data
        valid_data = StripePaymentIntentCreate(
            invoice_id=uuid4(),
            amount=Decimal("50.00"),
        )
        assert valid_data.amount == Decimal("50.00")

        # Invalid: too many decimal places
        with pytest.raises(ValueError, match="no more than 2 decimal places"):
            StripePaymentIntentCreate(
                invoice_id=uuid4(),
                amount=Decimal("50.123"),
            )


# ============================================================================
# Service Tests (with mocked Stripe)
# ============================================================================


class TestStripeProvider:
    """Tests for StripeProvider with mocked Stripe SDK."""

    @pytest.mark.asyncio
    @patch("stripe.PaymentIntent.create")
    async def test_create_payment_intent(self, mock_stripe_create):
        """Test creating a Stripe PaymentIntent."""
        # Mock Stripe response
        mock_stripe_create.return_value = MagicMock(
            id="pi_test123",
            client_secret="pi_test123_secret",
            status="requires_payment_method",
            amount=5000,
        )

        provider = StripeProvider()
        result = await provider.create_payment_intent(
            amount=Decimal("50.00"),
            metadata={"invoice_id": "test-invoice"},
        )

        assert result["id"] == "pi_test123"
        assert result["client_secret"] == "pi_test123_secret"
        assert result["amount"] == Decimal("50.00")
        assert result["status"] == "requires_payment_method"

        # Verify Stripe was called with correct params
        mock_stripe_create.assert_called_once()
        call_kwargs = mock_stripe_create.call_args[1]
        assert call_kwargs["amount"] == 5000  # Cents
        assert call_kwargs["currency"] == "usd"
        assert call_kwargs["metadata"]["invoice_id"] == "test-invoice"

    @pytest.mark.asyncio
    @patch("stripe.PaymentIntent.retrieve")
    async def test_retrieve_payment_intent(self, mock_stripe_retrieve):
        """Test retrieving a Stripe PaymentIntent."""
        # Mock Stripe response
        mock_charge = MagicMock()
        mock_charge.id = "ch_test123"
        mock_charge.payment_method_details.card.funding = "debit"

        mock_pi = MagicMock()
        mock_pi.id = "pi_test123"
        mock_pi.amount = 5000
        mock_pi.status = "succeeded"
        mock_pi.charges.data = [mock_charge]
        mock_pi.metadata = {}

        mock_stripe_retrieve.return_value = mock_pi

        provider = StripeProvider()
        result = await provider.retrieve_payment_intent("pi_test123")

        assert result["id"] == "pi_test123"
        assert result["amount"] == Decimal("50.00")
        assert result["payment_method"] == PaymentMethod.DEBIT_CARD
        assert result["charge_id"] == "ch_test123"

    @pytest.mark.asyncio
    @patch("stripe.Refund.create")
    async def test_refund_payment(self, mock_stripe_refund):
        """Test refunding a payment."""
        # Mock Stripe response
        mock_stripe_refund.return_value = MagicMock(
            id="re_test123",
            amount=5000,
            status="succeeded",
        )

        provider = StripeProvider()
        result = await provider.refund_payment(
            payment_intent_id="pi_test123",
            reason="Customer request",
        )

        assert result["id"] == "re_test123"
        assert result["amount"] == Decimal("50.00")
        assert result["status"] == "succeeded"

        mock_stripe_refund.assert_called_once()

    @patch("stripe.Webhook.construct_event")
    def test_verify_webhook_signature(self, mock_construct_event):
        """Test webhook signature verification."""
        mock_event = {"type": "payment_intent.succeeded", "data": {}}
        mock_construct_event.return_value = mock_event

        provider = StripeProvider()
        result = provider.verify_webhook_signature(
            payload=b"test_payload",
            signature="test_signature",
            secret="test_secret",
        )

        assert result == mock_event
        mock_construct_event.assert_called_once()

    # ============================================================================
    # NOTE: Service and integration tests requiring database fixtures are
    # commented out due to missing conftest.py setup. These tests verify:
    # - BillingService (invoice CRUD operations)
    # - PaymentService (payment intents, webhooks, refunds)
    # - Integration with database and Stripe provider
    #
    # TODO: Add conftest.py with db_session fixture to enable these tests
    # ============================================================================

    # @pytest.mark.asyncio
    # class TestBillingService:
    #     """Tests for BillingService."""
    #     ... (commented out for Phase 6 initial implementation)

    # @pytest.mark.asyncio
    # class TestPaymentService:
