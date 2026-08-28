from __future__ import annotations

from typing import Any, Dict, List

import pandas as pd


class RevenueAgent:
    """
    Detects revenue at risk from failed payment events.

    The agent preserves the original payment metadata so
    downstream Risk, Simulation, Decision, and Audit layers
    can use provider-specific information.
    """

    def __init__(
        self,
        payments_df: pd.DataFrame,
    ) -> None:

        self.payments = payments_df.copy()

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze payment data and identify recovery candidates.
        """

        if self.payments.empty:

            return {
                "total_payments": 0,
                "failed_payments": 0,
                "captured_payments": 0,
                "revenue_at_risk": 0.0,
                "failure_rate": 0.0,
                "recovery_candidates": [],
            }

        # ----------------------------------------------------
        # Normalize status safely
        # ----------------------------------------------------

        status = (
            self.payments["status"]
            .astype(str)
            .str.lower()
            .str.strip()
        )

        failed_mask = (
            status == "failed"
        )

        captured_mask = (
            status == "captured"
        )

        failed = self.payments[
            failed_mask
        ].copy()

        captured = self.payments[
            captured_mask
        ].copy()

        total_payments = len(
            self.payments
        )

        failed_count = len(
            failed
        )

        captured_count = len(
            captured
        )

        revenue_at_risk = float(
            failed["amount"].sum()
        )

        failure_rate = (
            failed_count
            / total_payments
            * 100
            if total_payments > 0
            else 0.0
        )

        # ----------------------------------------------------
        # Preserve ALL payment metadata
        # ----------------------------------------------------

        recovery_candidates: List[
            Dict[str, Any]
        ] = []

        for _, row in failed.iterrows():

            candidate = row.to_dict()

            # Normalize commonly used values.
            if "amount" in candidate:

                candidate["amount"] = float(
                    candidate["amount"]
                )

            if "retry_count" in candidate:

                try:

                    candidate["retry_count"] = int(
                        candidate["retry_count"]
                    )

                except (
                    ValueError,
                    TypeError,
                ):

                    candidate["retry_count"] = 0

            # Explicitly guarantee the core fields
            # expected by downstream agents.

            candidate.setdefault(
                "payment_id",
                None,
            )

            candidate.setdefault(
                "order_id",
                None,
            )

            candidate.setdefault(
                "customer_id",
                None,
            )

            candidate.setdefault(
                "payment_method",
                None,
            )

            candidate.setdefault(
                "failure_reason",
                None,
            )

            candidate.setdefault(
                "error_code",
                None,
            )

            candidate.setdefault(
                "error_description",
                None,
            )

            candidate.setdefault(
                "error_source",
                None,
            )

            candidate.setdefault(
                "error_step",
                None,
            )

            candidate.setdefault(
                "retry_count",
                0,
            )

            recovery_candidates.append(
                candidate
            )

        # Highest-value failed payments first.
        recovery_candidates.sort(
            key=lambda item: float(
                item.get(
                    "amount",
                    0,
                )
            ),
            reverse=True,
        )

        return {
            "total_payments":
                total_payments,

            "failed_payments":
                failed_count,

            "captured_payments":
                captured_count,

            "revenue_at_risk":
                revenue_at_risk,

            "failure_rate":
                failure_rate,

            "recovery_candidates":
                recovery_candidates,
        }