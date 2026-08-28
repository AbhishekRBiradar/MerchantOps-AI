from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


class RevenueAgent:
    """
    Detects revenue at risk from failed payment events.
    """

    def __init__(self, payments_df: pd.DataFrame) -> None:
        self.payments = payments_df.copy()

    def analyze(self) -> Dict[str, Any]:
        if self.payments.empty:
            return {
                "total_payments": 0,
                "failed_payments": 0,
                "captured_payments": 0,
                "revenue_at_risk": 0.0,
                "failure_rate": 0.0,
                "recovery_candidates": [],
            }

        total_payments = len(self.payments)

        failed = self.payments[
            self.payments["status"].str.lower() == "failed"
        ].copy()

        captured = self.payments[
            self.payments["status"].str.lower() == "captured"
        ]

        failed_count = len(failed)
        captured_count = len(captured)

        revenue_at_risk = float(
            failed["amount"].sum()
        )

        failure_rate = (
            failed_count / total_payments * 100
            if total_payments
            else 0.0
        )

        recovery_candidates: List[Dict[str, Any]] = []

        for _, row in failed.iterrows():
            recovery_candidates.append(
                {
                    "payment_id": str(row["payment_id"]),
                    "order_id": str(row["order_id"]),
                    "customer_id": str(row["customer_id"]),
                    "amount": float(row["amount"]),
                    "payment_method": str(
                        row["payment_method"]
                    ),
                    "failure_reason": str(
                        row["failure_reason"]
                    ),
                    "retry_count": int(
                        row["retry_count"]
                    ),
                }
            )

        recovery_candidates.sort(
            key=lambda item: item["amount"],
            reverse=True,
        )

        return {
            "total_payments": total_payments,
            "failed_payments": failed_count,
            "captured_payments": captured_count,
            "revenue_at_risk": revenue_at_risk,
            "failure_rate": failure_rate,
            "recovery_candidates": recovery_candidates,
        }