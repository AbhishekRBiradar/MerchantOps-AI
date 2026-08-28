from __future__ import annotations

from typing import Any, Dict, List


class SimulationAgent:
    """
    Simulates possible recovery actions for failed payments.

    This is a deterministic business simulation layer.
    It does not execute any payment action.
    """

    def simulate(
        self,
        risk_candidates: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:

        results: List[Dict[str, Any]] = []

        for candidate in risk_candidates:

            amount = float(
                candidate.get("amount", 0)
            )

            risk_score = float(
                candidate.get("risk_score", 0)
            )

            retry_count = int(
                candidate.get("retry_count", 0)
            )

            risk_level = str(
                candidate.get(
                    "risk_level",
                    "MEDIUM",
                )
            )

            # ----------------------------------------------
            # Estimate recovery probability.
            # ----------------------------------------------

            base_probability = 0.55 - (
                risk_score * 0.35
            )

            retry_penalty = min(
                retry_count * 0.08,
                0.24,
            )

            recovery_probability = max(
                0.05,
                base_probability - retry_penalty,
            )

            # ----------------------------------------------
            # Scenario 1: Retry Now
            # ----------------------------------------------

            retry_now_probability = max(
                0.05,
                recovery_probability,
            )

            retry_now_recovery = (
                amount
                * retry_now_probability
            )

            # ----------------------------------------------
            # Scenario 2: Retry Later
            # ----------------------------------------------

            retry_later_probability = max(
                0.03,
                recovery_probability * 0.75,
            )

            retry_later_recovery = (
                amount
                * retry_later_probability
            )

            # ----------------------------------------------
            # Scenario 3: Do Nothing
            # ----------------------------------------------

            do_nothing_probability = 0.08

            do_nothing_recovery = (
                amount
                * do_nothing_probability
            )

            scenarios = [
                {
                    "action": "RETRY_NOW",
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
                    "expected_recovery": round(
                        retry_later_recovery,
                        2,
                    ),
                    "risk": round(
                        max(
                            risk_score - 0.05,
                            0,
                        ),
                        3,
                    ),
                },
                {
                    "action": "DO_NOTHING",
                    "expected_recovery": round(
                        do_nothing_recovery,
                        2,
                    ),
                    "risk": 0.0,
                },
            ]

            # ----------------------------------------------
            # Safety rule:
            # High-risk candidates should not automatically
            # select a retry even if expected recovery is high.
            # ----------------------------------------------

            if risk_level == "HIGH":

                best = max(
                    scenarios,
                    key=lambda item: (
                        item["expected_recovery"]
                        if item["action"] == "DO_NOTHING"
                        else 0
                    ),
                )

                best["action"] = "DO_NOTHING"

            else:

                best = max(
                    scenarios,
                    key=lambda item:
                        item["expected_recovery"]
                        - (
                            item["risk"]
                            * amount
                        ),
                )

            result = dict(candidate)

            result.update(
                {
                    "simulation_scenarios":
                        scenarios,
                    "recommended_action":
                        best["action"],
                    "expected_recovery":
                        best["expected_recovery"],
                    "simulation_risk":
                        best["risk"],
                }
            )

            results.append(result)

        return results