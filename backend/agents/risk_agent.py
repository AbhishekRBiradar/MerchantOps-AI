from __future__ import annotations

from typing import Any, Dict, List


class RiskAgent:
    """
    Evaluates payment-recovery candidates and assigns
    a risk score and recommended action.
    """

    FAILURE_RISK = {
        "network_error": 0.15,
        "bank_error": 0.30,
        "authentication_failed": 0.45,
        "insufficient_funds": 0.65,
        "limit_exceeded": 0.55,
    }

    METHOD_RISK = {
        "UPI": 0.05,
        "CARD": 0.10,
        "NETBANKING": 0.15,
        "WALLET": 0.10,
    }

    def evaluate(
        self,
        recovery_candidates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        results: List[Dict[str, Any]] = []

        for candidate in recovery_candidates:

            failure_reason = str(
                candidate.get(
                    "failure_reason",
                    "",
                )
            ).lower()

            payment_method = str(
                candidate.get(
                    "payment_method",
                    "",
                )
            ).upper()

            retry_count = int(
                candidate.get(
                    "retry_count",
                    0,
                )
            )

            amount = float(
                candidate.get(
                    "amount",
                    0,
                )
            )

            risk_score = self.FAILURE_RISK.get(
                failure_reason,
                0.40,
            )

            risk_score += self.METHOD_RISK.get(
                payment_method,
                0.10,
            )

            risk_score += min(
                retry_count * 0.12,
                0.36,
            )

            # Higher-value failed payments receive
            # a small additional review factor.
            if amount >= 5000:
                risk_score += 0.05

            risk_score = min(
                risk_score,
                1.0,
            )

            if risk_score < 0.30:
                risk_level = "LOW"
                action = "RETRY"

            elif risk_score < 0.60:
                risk_level = "MEDIUM"
                action = "REVIEW"

            else:
                risk_level = "HIGH"
                action = "DO_NOT_RETRY"

            result = dict(candidate)

            result.update(
                {
                    "risk_score": round(
                        risk_score,
                        3,
                    ),
                    "risk_level": risk_level,
                    "recommended_action": action,
                }
            )

            results.append(result)

        return results