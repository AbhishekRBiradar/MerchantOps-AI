from __future__ import annotations

from typing import Any, Dict, List


class DecisionAgent:
    """
    Converts risk and simulation results into a final,
    explainable merchant decision.

    This agent recommends actions only.
    It does not execute payment operations.
    """

    def decide(
        self,
        simulated_candidates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        results: List[Dict[str, Any]] = []

        for candidate in simulated_candidates:

            risk_level = str(
                candidate.get(
                    "risk_level",
                    "MEDIUM",
                )
            ).upper()

            risk_score = float(
                candidate.get(
                    "risk_score",
                    0.5,
                )
            )

            simulation_action = str(
                candidate.get(
                    "recommended_action",
                    "DO_NOTHING",
                )
            ).upper()

            expected_recovery = float(
                candidate.get(
                    "expected_recovery",
                    0.0,
                )
            )

            amount = float(
                candidate.get(
                    "amount",
                    0.0,
                )
            )

            # ------------------------------------------------
            # Final decision policy
            # ------------------------------------------------

            if risk_level == "HIGH":

                final_action = "DO_NOTHING"

                approval_required = False

                reason = (
                    "Risk is too high for an "
                    "automatic recovery action."
                )

            elif simulation_action == "RETRY_NOW":

                final_action = "RETRY_NOW"

                approval_required = True

                reason = (
                    "Simulation indicates strong "
                    "recovery potential, but payment "
                    "retry requires merchant approval."
                )

            elif simulation_action == "RETRY_LATER":

                final_action = "RETRY_LATER"

                approval_required = True

                reason = (
                    "A delayed retry provides a "
                    "reasonable recovery opportunity "
                    "with lower immediate risk."
                )

            else:

                final_action = "REVIEW"

                approval_required = True

                reason = (
                    "The recovery opportunity is "
                    "not strong enough for automatic "
                    "execution."
                )

            # ------------------------------------------------
            # Additional safety rule
            # ------------------------------------------------

            if (
                final_action == "RETRY_NOW"
                and risk_score >= 0.50
            ):

                final_action = "REVIEW"

                approval_required = True

                reason = (
                    "Recovery potential exists, but "
                    "risk is high enough to require "
                    "manual review before retry."
                )

            # ------------------------------------------------
            # Recovery opportunity ratio
            # ------------------------------------------------

            recovery_ratio = (
                expected_recovery / amount
                if amount > 0
                else 0.0
            )

            result = dict(candidate)

            result.update(
                {
                    "final_action":
                        final_action,

                    "approval_required":
                        approval_required,

                    "decision_reason":
                        reason,

                    "recovery_ratio":
                        round(
                            recovery_ratio,
                            3,
                        ),

                    "decision_confidence":
                        round(
                            max(
                                0.0,
                                min(
                                    1.0,
                                    1.0 - risk_score,
                                ),
                            ),
                            3,
                        ),
                }
            )

            results.append(result)

        return results