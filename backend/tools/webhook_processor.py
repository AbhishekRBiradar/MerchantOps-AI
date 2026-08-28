from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from backend.agents.orchestrator import MerchantOpsOrchestrator
from backend.database.audit import AuditLogger
from razorpay.client import RazorpayClient
from razorpay.payment_adapter import RazorpayPaymentAdapter


class RazorpayWebhookProcessor:
    """
    Converts a verified Razorpay webhook into a MerchantOps
    processing event.
    """

    def __init__(
        self,
        client: RazorpayClient | None = None,
        adapter: RazorpayPaymentAdapter | None = None,
        audit_logger: AuditLogger | None = None,
    ) -> None:

        self.client = (
            client
            or RazorpayClient()
        )

        self.adapter = (
            adapter
            or RazorpayPaymentAdapter(
                client=self.client
            )
        )

        self.audit_logger = (
            audit_logger
            or AuditLogger()
        )

    def process(
        self,
        event_name: str,
        payment_id: str | None,
    ) -> Dict[str, Any]:
        """
        Process a Razorpay webhook event.

        For payment events, the latest payment object is
        fetched directly from Razorpay and passed through
        the MerchantOps pipeline.
        """

        event_name = str(
            event_name
            or "unknown"
        ).strip()

        if not payment_id:

            return {
                "processed": False,
                "event": event_name,
                "reason": (
                    "Webhook does not contain "
                    "a payment ID."
                ),
            }

        # ----------------------------------------------------
        # Fetch latest payment from Razorpay
        # ----------------------------------------------------

        payment = self.client.fetch_payment(
            payment_id
        )

        # ----------------------------------------------------
        # Normalize Razorpay payment
        # ----------------------------------------------------

        normalized_payment = (
            self.adapter.normalize_payment(
                payment
            )
        )

        # ----------------------------------------------------
        # Run MerchantOps on this payment
        # ----------------------------------------------------

        payment_df = pd.DataFrame(
            [normalized_payment]
        )

        result = (
            MerchantOpsOrchestrator(
                payment_df
            ).run()
        )

        # ----------------------------------------------------
        # Record processing event
        # ----------------------------------------------------

        self.audit_logger.log_event(
            event_type="WEBHOOK_PROCESSING",
            payment_id=payment_id,
            action=event_name,
            status="PROCESSED",
            details={
                "payment_status":
                    normalized_payment.get(
                        "status"
                    ),

                "amount":
                    normalized_payment.get(
                        "amount"
                    ),

                "risk_level":
                    (
                        result[
                            "decision_records"
                        ][0].get(
                            "risk_level"
                        )
                        if result[
                            "decision_records"
                        ]
                        else None
                    ),

                "final_action":
                    (
                        result[
                            "decision_records"
                        ][0].get(
                            "final_action"
                        )
                        if result[
                            "decision_records"
                        ]
                        else None
                    ),

                "merchantops_result":
                    result,
            },
        )

        return {
            "processed": True,
            "event": event_name,
            "payment_id": payment_id,
            "payment_status":
                normalized_payment.get(
                    "status"
                ),
            "merchantops": result,
        }