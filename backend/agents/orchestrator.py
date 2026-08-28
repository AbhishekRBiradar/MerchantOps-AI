from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from backend.agents.revenue_agent import RevenueAgent
from backend.agents.risk_agent import RiskAgent
from backend.agents.simulation_agent import SimulationAgent
from backend.agents.decision_agent import DecisionAgent


class MerchantOpsOrchestrator:
    """
    Coordinates the MerchantOps AI agent pipeline.

    Pipeline:

        Payment Data
            ↓
        Revenue Agent
            ↓
        Risk Agent
            ↓
        Simulation Agent
            ↓
        Decision Agent
            ↓
        Final Merchant Intelligence
    """

    def __init__(
        self,
        payments_df: pd.DataFrame,
    ) -> None:

        self.payments_df = payments_df

        self.revenue_agent = RevenueAgent(
            payments_df
        )

        self.risk_agent = RiskAgent()

        self.simulation_agent = (
            SimulationAgent()
        )

        self.decision_agent = (
            DecisionAgent()
        )

    def run(self) -> Dict[str, Any]:
        """
        Execute the complete MerchantOps pipeline.
        """

        # ---------------------------------------------
        # Stage 1: Revenue analysis
        # ---------------------------------------------

        revenue_result = (
            self.revenue_agent.analyze()
        )

        recovery_candidates = (
            revenue_result[
                "recovery_candidates"
            ]
        )

        # ---------------------------------------------
        # Stage 2: Risk evaluation
        # ---------------------------------------------

        risk_result = (
            self.risk_agent.evaluate(
                recovery_candidates
            )
        )

        # ---------------------------------------------
        # Stage 3: Action simulation
        # ---------------------------------------------

        simulation_result = (
            self.simulation_agent.simulate(
                risk_result
            )
        )

        # ---------------------------------------------
        # Stage 4: Final decision
        # ---------------------------------------------

        decision_result = (
            self.decision_agent.decide(
                simulation_result
            )
        )

        # ---------------------------------------------
        # Aggregate action counts
        # ---------------------------------------------

        action_counts = {
            "RETRY_NOW": 0,
            "RETRY_LATER": 0,
            "REVIEW": 0,
            "DO_NOTHING": 0,
        }

        for decision in decision_result:

            action = str(
                decision.get(
                    "final_action",
                    "DO_NOTHING",
                )
            ).upper()

            if action in action_counts:
                action_counts[action] += 1

        # ---------------------------------------------
        # Build final response
        # ---------------------------------------------

        return {
            "operations": {
                "total_payments":
                    revenue_result[
                        "total_payments"
                    ],

                "failed_payments":
                    revenue_result[
                        "failed_payments"
                    ],

                "captured_payments":
                    revenue_result[
                        "captured_payments"
                    ],

                "failure_rate":
                    revenue_result[
                        "failure_rate"
                    ],

                "revenue_at_risk":
                    revenue_result[
                        "revenue_at_risk"
                    ],
            },

            "recovery_candidates":
                len(recovery_candidates),

            "action_counts":
                action_counts,

            "decisions":
                decision_result,
        }