from __future__ import annotations

from typing import Any, Dict

import pandas as pd

from backend.agents.revenue_agent import RevenueAgent
from backend.agents.risk_agent import RiskAgent
from backend.agents.simulation_agent import SimulationAgent
from backend.agents.decision_agent import DecisionAgent
from backend.tools.action_tools import evaluate_action
from backend.database.audit import AuditLogger


class MerchantOpsOrchestrator:
    """
    Coordinates the complete MerchantOps AI workflow.

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
    Action Policy
        ↓
    Audit Logger
    """

    def __init__(
        self,
        payments_df: pd.DataFrame,
        audit_logger: AuditLogger | None = None,
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

        self.audit_logger = (
            audit_logger
            or AuditLogger()
        )

    def run(self) -> Dict[str, Any]:
        """
        Execute the complete MerchantOps pipeline.
        """

        # --------------------------------------------------
        # 1. Revenue analysis
        # --------------------------------------------------

        revenue_result = (
            self.revenue_agent.analyze()
        )

        recovery_candidates = (
            revenue_result[
                "recovery_candidates"
            ]
        )

        # --------------------------------------------------
        # 2. Risk assessment
        # --------------------------------------------------

        risk_result = (
            self.risk_agent.evaluate(
                recovery_candidates
            )
        )

        # --------------------------------------------------
        # 3. Simulation
        # --------------------------------------------------

        simulation_result = (
            self.simulation_agent.simulate(
                risk_result
            )
        )

        # --------------------------------------------------
        # 4. Final decisions
        # --------------------------------------------------

        decision_result = (
            self.decision_agent.decide(
                simulation_result
            )
        )

        # --------------------------------------------------
        # 5. Apply action policy + audit
        # --------------------------------------------------

        governed_decisions = []

        for decision in decision_result:

            policy_result = evaluate_action(
                decision
            )

            self.audit_logger.log_decision(
                decision
            )

            self.audit_logger.log_policy_result(
                decision,
                policy_result,
            )

            governed_decision = dict(
                decision
            )

            governed_decision[
                "policy"
            ] = policy_result

            governed_decisions.append(
                governed_decision
            )

        # --------------------------------------------------
        # 6. Action summary
        # --------------------------------------------------

        final_action_counts = {
            "RETRY_NOW": 0,
            "RETRY_LATER": 0,
            "REVIEW": 0,
            "DO_NOTHING": 0,
        }

        execution_modes = {
            "MERCHANT_APPROVAL": 0,
            "SCHEDULED_TEST_ACTION": 0,
            "BLOCKED": 0,
            "NO_ACTION": 0,
        }

        approval_required = 0

        allowed_actions = 0

        blocked_actions = 0

        for decision in governed_decisions:

            action = str(
                decision.get(
                    "final_action",
                    "DO_NOTHING",
                )
            ).upper()

            if action in final_action_counts:

                final_action_counts[
                    action
                ] += 1

            policy = decision[
                "policy"
            ]

            mode = policy.get(
                "execution_mode",
                "BLOCKED",
            )

            if mode in execution_modes:

                execution_modes[
                    mode
                ] += 1

            if policy.get(
                "approval_required",
                False,
            ):

                approval_required += 1

            if policy.get(
                "allowed",
                False,
            ):

                allowed_actions += 1

            else:

                blocked_actions += 1

        # --------------------------------------------------
        # 7. Final response
        # --------------------------------------------------

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
                len(
                    recovery_candidates
                ),

            "risk_candidates":
                len(
                    risk_result
                ),

            "simulated_candidates":
                len(
                    simulation_result
                ),

            "decisions":
                len(
                    governed_decisions
                ),

            "action_counts":
                final_action_counts,

            "execution_modes":
                execution_modes,

            "approval_required":
                approval_required,

            "allowed_actions":
                allowed_actions,

            "blocked_actions":
                blocked_actions,

            "decision_records":
                governed_decisions,
        }