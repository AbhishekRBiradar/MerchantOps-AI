from __future__ import annotations

from typing import Any, Dict, List


class SimulationAgent:
    """
    Simulates possible revenue-recovery actions.

    The agent does not execute payments.
    It estimates outcomes so that the Decision Agent
    can later choose a controlled action.
    """

    FAILURE_BASE_PROBABILITY = {
        "network_error": 0.70,
        "bank_error": 0.50,
        "authentication_failed": 0.35,
        "insufficient_funds": 0.20,
        "limit_exceeded": 0.25,
    }

    def simulate(
        self,
        risk_candidates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
    
        results = []

        for candidate in risk_candidates:

            amount = float(
                candidate.get("amount", 0.0)
            )

            risk_score = float(
                candidate.get("risk_score", 0.5)
            )

            risk_level = str(
                candidate.get(
                    "risk_level",
                    "MEDIUM",
                )
            ).upper()

            failure_reason = str(
                candidate.get(
                    "failure_reason",
                    "",
                )
            ).lower()

            retry_count = int(
                candidate.get(
                    "retry_count",
                    0,
                )
            )

            base_probability = (
                self.FAILURE_BASE_PROBABILITY.get(
                    failure_reason,
                    0.40,
                )
            )

            # Repeated retries reduce expected recovery.
            retry_penalty = min(
                retry_count * 0.12,
                0.36,
            )

            base_probability = max(
                0.05,
                base_probability - retry_penalty,
            )

            # Risk slightly reduces recovery confidence.
            risk_adjustment = (
                risk_score * 0.15
            )

            retry_now_probability = max(
                0.05,
                base_probability - risk_adjustment,
            )

            retry_later_probability = max(
                0.03,
                retry_now_probability * 0.75,
            )

            do_nothing_probability = 0.05

            retry_now_recovery = (
                amount
                * retry_now_probability
            )

            retry_later_recovery = (
                amount
                * retry_later_probability
            )

            do_nothing_recovery = (
                amount
                * do_nothing_probability
            )

            scenarios = [
                {
                    "action": "RETRY_NOW",
                    "probability": round(
                        retry_now_probability,
                        3,
                    ),
                    "expected_recovery": round(
                        retry_now_recovery,
                        2,
                    ),
                    "risk": round(
                        risk_score,
                        3,
                    ),
                },
                {
                    "action": "RETRY_LATER",
                    "probability": round(
                        retry_later_probability,
                        3,
                    ),
                    "expected_recovery": round(
                        retry_later_recovery,
                        2,
                    ),
                    "risk": round(
                        max(
                            risk_score - 0.05,
                            0.0,
                        ),
                        3,
                    ),
                },
                {
                    "action": "DO_NOTHING",
                    "probability": do_nothing_probability,
                    "expected_recovery": round(
                        do_nothing_recovery,
                        2,
                    ),
                    "risk": 0.0,
                },
            ]

            # ------------------------------------------------
            # Choose the strategy using business policy.
            # ------------------------------------------------

            if risk_level == "HIGH":

                recommended_action = (
                    "DO_NOTHING"
                )

            elif risk_level == "MEDIUM":

                if (
                    retry_now_probability >= 0.45
                    and retry_count == 0
                ):
                    recommended_action = (
                        "RETRY_NOW"
                    )

                elif (
                    retry_later_probability >= 0.25
                ):
                    recommended_action = (
                        "RETRY_LATER"
                    )

                else:
                    recommended_action = (
                        "DO_NOTHING"
                    )

            else:

                if retry_now_probability >= 0.30:

                    recommended_action = (
                        "RETRY_NOW"
                    )

                elif (
                    retry_later_probability >= 0.20
                ):

                    recommended_action = (
                        "RETRY_LATER"
                    )

                else:

                    recommended_action = (
                        "DO_NOTHING"
                    )

            selected = next(
                scenario
                for scenario in scenarios
                if scenario["action"]
                == recommended_action
            )

            result = dict(candidate)

            result.update(
                {
                    "simulation_scenarios": scenarios,
                    "recommended_action":
                        recommended_action,
                    "expected_recovery":
                        selected[
                            "expected_recovery"
                        ],
                    "simulation_risk":
                        selected["risk"],
                    "recovery_probability":
                        selected["probability"],
                }
            )

            results.append(result)

        return results