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
                    "method": "upi",
                    "status": "failed",
                    "error_reason":
                        "network_error",
                    "created_at": 1234567890,
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

    assert payment["payment_id"] == "pay_test_001"
    assert payment["amount"] == 2500.0
    assert payment["payment_method"] == "UPI"
    assert payment["status"] == "failed"
    assert (
        payment["failure_reason"]
        == "network_error"
    )