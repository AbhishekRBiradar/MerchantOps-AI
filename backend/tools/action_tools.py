from __future__ import annotations

from typing import Any, Dict


class ActionPolicy:
    """
    Determines whether an AI-recommended action can be executed,
    requires merchant approval, or must be blocked.

    This layer does not execute payment actions.
    It only applies safety and business rules.
    """

    AUTO_ACTIONS = {
        "RETRY_LATER",
    }

    APPROVAL_ACTIONS = {
        "RETRY_NOW",
        "RETRY_LATER",
        "REVIEW",
    }

    BLOCKED_ACTIONS = {
        "DO_NOTHING",
    }

    def evaluate(
        self,
        decision: Dict[str, Any],
    ) -> Dict[str, Any]:

        action = str(
            decision.get(
                "final_action",
                "DO_NOTHING",
            )
        ).upper()

        risk_level = str(
            decision.get(
                "risk_level",
                "MEDIUM",
            )
        ).upper()

        risk_score = float(
            decision.get(
                "risk_score",
                0.0,
            )
        )

        amount = float(
            decision.get(
                "amount",
                0.0,
            )
        )

        # --------------------------------------------------
        # High-risk actions are blocked.
        # --------------------------------------------------

        if risk_level == "HIGH" or risk_score >= 0.75:

            return {
                "allowed": False,
                "approval_required": False,
                "execution_mode": "BLOCKED",
                "action": action,
                "reason": (
                    "Action blocked because the "
                    "transaction risk is too high."
                ),
            }

        # --------------------------------------------------
        # No-op decisions do not require execution.
        # --------------------------------------------------

        if action == "DO_NOTHING":

            return {
                "allowed": False,
                "approval_required": False,
                "execution_mode": "NO_ACTION",
                "action": action,
                "reason": (
                    "No payment action is recommended."
                ),
            }

        # --------------------------------------------------
        # Large payment retries always require approval.
        # --------------------------------------------------

        if (
            action == "RETRY_NOW"
            and amount >= 5000
        ):

            return {
                "allowed": True,
                "approval_required": True,
                "execution_mode": "MERCHANT_APPROVAL",
                "action": action,
                "reason": (
                    "High-value payment retry "
                    "requires merchant approval."
                ),
            }

        # --------------------------------------------------
        # Retry Now normally requires approval.
        # --------------------------------------------------

        if action == "RETRY_NOW":

            return {
                "allowed": True,
                "approval_required": True,
                "execution_mode": "MERCHANT_APPROVAL",
                "action": action,
                "reason": (
                    "Immediate payment retry "
                    "requires merchant approval."
                ),
            }

        # --------------------------------------------------
        # Retry Later can be queued, but remains bounded.
        # --------------------------------------------------

        if action == "RETRY_LATER":

            return {
                "allowed": True,
                "approval_required": False,
                "execution_mode": "SCHEDULED_TEST_ACTION",
                "action": action,
                "reason": (
                    "Delayed retry can be scheduled "
                    "as a bounded test action."
                ),
            }

        # --------------------------------------------------
        # Review always requires merchant approval.
        # --------------------------------------------------

        if action == "REVIEW":

            return {
                "allowed": True,
                "approval_required": True,
                "execution_mode": "MERCHANT_APPROVAL",
                "action": action,
                "reason": (
                    "Manual merchant review is required."
                ),
            }

        # --------------------------------------------------
        # Unknown actions are blocked.
        # --------------------------------------------------

        return {
            "allowed": False,
            "approval_required": False,
            "execution_mode": "BLOCKED",
            "action": action,
            "reason": (
                "Unknown action rejected by policy."
            ),
        }


def evaluate_action(
    decision: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Convenience function for evaluating one decision.
    """

    policy = ActionPolicy()

    return policy.evaluate(
        decision
    )