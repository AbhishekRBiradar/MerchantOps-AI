import pandas as pd

from backend.tools.webhook_processor import (
    RazorpayWebhookProcessor,
)


class FakeClient:

    def fetch_payment(
        self,
        payment_id,
    ):
        return {
            "id": payment_id,
            "order_id": "order_test_001",
            "amount": 100000,
            "currency": "INR",
            "status": "failed",
            "method": "netbanking",
            "email": "test@example.com",
            "error_code":
                "BAD_REQUEST_ERROR",
            "error_description":
                "Payment declined by bank",
            "error_source":
                "bank",
            "error_step":
                "payment_authorization",
            "error_reason":
                "payment_failed",
            "created_at":
                1234567890,
        }


class FakeAdapter:

    def __init__(self, client=None):
        pass

    def normalize_payment(
        self,
        payment,
    ):
        return {
            "payment_id":
                payment["id"],

            "order_id":
                payment["order_id"],

            "customer_id":
                payment["email"],

            "amount": 1000.0,

            "payment_method":
                "NETBANKING",

            "status":
                "failed",

            "failure_reason":
                "payment_failed",

            "error_code":
                "BAD_REQUEST_ERROR",

            "error_description":
                "Payment declined by bank",

            "error_source":
                "bank",

            "error_step":
                "payment_authorization",

            "created_at":
                1234567890,

            "retry_count": 0,
        }


class FakeAuditLogger:

    def __init__(self):
        self.events = []

    def log_event(
        self,
        **kwargs,
    ):
        self.events.append(
            kwargs
        )

        return {
            "recorded": True
        }


def test_webhook_processor():

    audit = FakeAuditLogger()

    processor = RazorpayWebhookProcessor(
        client=FakeClient(),
        adapter=FakeAdapter(),
        audit_logger=audit,
    )

    result = processor.process(
        event_name="payment.failed",
        payment_id="pay_test_001",
    )

    assert result["processed"] is True

    assert (
        result["payment_id"]
        == "pay_test_001"
    )

    assert (
        result["payment_status"]
        == "failed"
    )

    assert (
        result["merchantops"]
        is not None
    )

    assert len(audit.events) == 1

    assert (
        audit.events[0]["event_type"]
        == "WEBHOOK_PROCESSING"
    )