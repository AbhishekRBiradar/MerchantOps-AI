from __future__ import annotations

from typing import Any, Dict, List


class RiskAgent:
    """
    Evaluates payment-recovery candidates.

    The agent supports both:
    - Synthetic MerchantOps payment data
    - Razorpay payment failure metadata
    """

    FAILURE_RISK = {
        "network_error": 0.15,
        "bank_error": 0.30,
        "authentication_failed": 0.45,
        "insufficient_funds": 0.65,
        "limit_exceeded": 0.55,
        "payment_failed": 0.40,
    }

    METHOD_RISK = {
        "UPI": 0.05,
        "CARD": 0.10,
        "NETBANKING": 0.15,
        "WALLET": 0.10,
    }

    RAZORPAY_SOURCE_RISK = {
        "bank": 0.15,
        "gateway": 0.10,
        "customer": 0.20,
        "internal": 0.25,
    }

    RAZORPAY_STEP_RISK = {
        "payment_authorization": 0.15,
        "payment_authentication": 0.10,
        "payment_capture": 0.05,
        "payment_initiation": 0.05,
    }

    def evaluate(
        self,
        recovery_candidates: List[
            Dict[str, Any]
        ],
    ) -> List[Dict[str, Any]]:
        """
        Evaluate recovery candidates and assign:
        risk_score
        risk_level
        recommended_action
        """

        results: List[Dict[str, Any]] = []

        for candidate in recovery_candidates:

            failure_reason = str(
                candidate.get(
                    "failure_reason",
                    "",
                )
            ).lower().strip()

            payment_method = str(
                candidate.get(
                    "payment_method",
                    "",
                )
            ).upper().strip()

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

            error_source = str(
                candidate.get(
                    "error_source",
                    "",
                )
            ).lower().strip()

            error_step = str(
                candidate.get(
                    "error_step",
                    "",
                )
            ).lower().strip()

            error_code = str(
                candidate.get(
                    "error_code",
                    "",
                )
            ).upper().strip()

            # ------------------------------------------------
            # Base failure risk
            # ------------------------------------------------

            risk_score = (
                self.FAILURE_RISK.get(
                    failure_reason,
                    0.40,
                )
            )

            # ------------------------------------------------
            # Payment method risk
            # ------------------------------------------------

            risk_score += (
                self.METHOD_RISK.get(
                    payment_method,
                    0.10,
                )
            )

            # ------------------------------------------------
            # Razorpay error source risk
            # ------------------------------------------------

            risk_score += (
                self.RAZORPAY_SOURCE_RISK.get(
                    error_source,
                    0.0,
                )
            )

            # ------------------------------------------------
            # Razorpay error step risk
            # ------------------------------------------------

            risk_score += (
                self.RAZORPAY_STEP_RISK.get(
                    error_step,
                    0.0,
                )
            )

            # ------------------------------------------------
            # Authentication-related API errors
            # ------------------------------------------------

            if (
                error_code
                == "BAD_REQUEST_ERROR"
                and error_step
                in {
                    "payment_authorization",
                    "payment_authentication",
                }
            ):
                risk_score += 0.10

            # ------------------------------------------------
            # Repeated retries increase risk
            # ------------------------------------------------

            risk_score += min(
                retry_count * 0.12,
                0.36,
            )

            # ------------------------------------------------
            # High-value transaction factor
            # ------------------------------------------------

            if amount >= 5000:
                risk_score += 0.05

            # ------------------------------------------------
            # Clamp score
            # ------------------------------------------------

            risk_score = min(
                risk_score,
                1.0,
            )

            # ------------------------------------------------
            # Risk classification
            # ------------------------------------------------

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

                    "risk_level":
                        risk_level,

                    "recommended_action":
                        action,
                }
            )

            results.append(result)

        return results