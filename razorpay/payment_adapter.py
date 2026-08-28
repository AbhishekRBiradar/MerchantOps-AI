from __future__ import annotations

from typing import Any, Dict, List

from razorpay.client import RazorpayClient


class RazorpayPaymentAdapter:
    """
    Converts Razorpay payment responses into the
    normalized structure expected by MerchantOps AI.
    """

    def __init__(
        self,
        client: RazorpayClient | None = None,
    ) -> None:

        self.client = (
            client
            or RazorpayClient()
        )

    def fetch_payments(
        self,
        count: int = 10,
    ) -> List[Dict[str, Any]]:

        response = self.client.fetch_payments(
            count=count
        )

        items = response.get(
            "items",
            []
        )

        normalized = []

        for payment in items:

            normalized.append(
                {
                    "payment_id":
                        payment.get("id"),

                    "order_id":
                        payment.get("order_id"),

                    "customer_id":
                        None,

                    "amount":
                        float(
                            payment.get(
                                "amount",
                                0,
                            )
                        ) / 100,

                    "payment_method":
                        str(
                            payment.get(
                                "method",
                                "",
                            )
                        ).upper(),

                    "status":
                        str(
                            payment.get(
                                "status",
                                "",
                            )
                        ).lower(),

                    "failure_reason":
                        payment.get(
                            "error_reason"
                        ),

                    "created_at":
                        payment.get(
                            "created_at"
                        ),

                    "retry_count":
                        0,
                }
            )

        return normalized