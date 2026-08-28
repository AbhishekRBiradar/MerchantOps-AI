from __future__ import annotations

from typing import Any, Dict, List

from razorpay.client import RazorpayClient


class RazorpayPaymentAdapter:
    """
    Converts Razorpay payment responses into the normalized
    payment structure expected by MerchantOps AI.
    """

    def __init__(
        self,
        client: RazorpayClient | None = None,
    ) -> None:

        self.client = (
            client
            or RazorpayClient()
        )

    def normalize_payment(
        self,
        payment: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Normalize one Razorpay payment object.
        """

        amount = float(
            payment.get(
                "amount",
                0,
            )
        ) / 100

        status = str(
            payment.get(
                "status",
                "",
            )
        ).lower()

        method = str(
            payment.get(
                "method",
                "",
            )
        ).upper()

        error_reason = payment.get(
            "error_reason"
        )

        error_code = payment.get(
            "error_code"
        )

        error_description = payment.get(
            "error_description"
        )

        error_source = payment.get(
            "error_source"
        )

        error_step = payment.get(
            "error_step"
        )

        return {
            "payment_id":
                payment.get("id"),

            "order_id":
                payment.get("order_id"),

            "customer_id":
                payment.get("email"),

            "amount":
                amount,

            "payment_method":
                method,

            "status":
                status,

            "failure_reason":
                error_reason,

            "error_code":
                error_code,

            "error_description":
                error_description,

            "error_source":
                error_source,

            "error_step":
                error_step,

            "created_at":
                payment.get(
                    "created_at"
                ),

            "retry_count":
                0,
        }

    def fetch_payments(
        self,
        count: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Fetch and normalize Razorpay payments.
        """

        response = (
            self.client.fetch_payments(
                count=count
            )
        )

        items = response.get(
            "items",
            []
        )

        return [
            self.normalize_payment(
                payment
            )
            for payment in items
        ]