from razorpay.payment_adapter import (
    RazorpayPaymentAdapter,
)


class FakeClient:

    def fetch_payments(
        self,
        count=10,
    ):

        return {
            "items": [
                {
                    "id": "pay_test_001",
                    "order_id": "order_test_001",
                    "amount": 250000,
                    "method": "netbanking",
                    "status": "failed",
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
                    "email":
                        "test@example.com",
                    "created_at":
                        1234567890,
                }
            ]
        }


def test_payment_normalization():

    adapter = RazorpayPaymentAdapter(
        client=FakeClient()
    )

    payments = adapter.fetch_payments(
        count=1
    )

    assert len(payments) == 1

    payment = payments[0]

    assert (
        payment["payment_id"]
        == "pay_test_001"
    )

    assert (
        payment["amount"]
        == 2500.0
    )

    assert (
        payment["payment_method"]
        == "NETBANKING"
    )

    assert (
        payment["status"]
        == "failed"
    )

    assert (
        payment["failure_reason"]
        == "payment_failed"
    )

    assert (
        payment["error_code"]
        == "BAD_REQUEST_ERROR"
    )

    assert (
        payment["error_source"]
        == "bank"
    )

    assert (
        payment["error_step"]
        == "payment_authorization"
    )