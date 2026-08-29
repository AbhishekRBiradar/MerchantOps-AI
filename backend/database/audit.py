from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.database.postgres import PostgresDatabase


AUDIT_FILE = Path(
    "data/audit_log.jsonl"
)


class AuditLogger:
    """
    Append-only audit logger for MerchantOps AI.

    Behavior:

    Local development without DATABASE_URL:
        data/audit_log.jsonl

    Production with DATABASE_URL:
        PostgreSQL audit_logs table
    """

    def __init__(
        self,
        file_path: Path = AUDIT_FILE,
        database: Optional[PostgresDatabase] = None,
    ) -> None:

        self.file_path = file_path

        self.database = database

        # ----------------------------------------------------
        # Use PostgreSQL when DATABASE_URL exists.
        # ----------------------------------------------------

        database_url = os.getenv(
            "DATABASE_URL"
        )

        if (
            self.database is None
            and database_url
        ):

            self.database = (
                PostgresDatabase(
                    database_url
                )
            )

            self.database.initialize()

        # ----------------------------------------------------
        # Local file fallback.
        # ----------------------------------------------------

        if self.database is None:

            self.file_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

    # ========================================================
    # LOG EVENT
    # ========================================================

    def log_event(
        self,
        event_type: str,
        payment_id: Optional[str] = None,
        decision: Optional[str] = None,
        action: Optional[str] = None,
        risk_level: Optional[str] = None,
        approval_required: Optional[bool] = None,
        execution_mode: Optional[str] = None,
        status: str = "RECORDED",
        details: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        event = {
            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "event_type":
                event_type,

            "payment_id":
                payment_id,

            "decision":
                decision,

            "action":
                action,

            "risk_level":
                risk_level,

            "approval_required":
                approval_required,

            "execution_mode":
                execution_mode,

            "status":
                status,

            "details":
                details or {},
        }

        # ----------------------------------------------------
        # PostgreSQL mode
        # ----------------------------------------------------

        if self.database is not None:

            self.database.insert_audit_event(
                event
            )

            return event

        # ----------------------------------------------------
        # File mode
        # ----------------------------------------------------

        with self.file_path.open(
            "a",
            encoding="utf-8",
        ) as file:

            file.write(
                json.dumps(
                    event,
                    default=str,
                )
                + "\n"
            )

        return event

    # ========================================================
    # LOG AI DECISION
    # ========================================================

    def log_decision(
        self,
        decision: Dict[str, Any],
    ) -> Dict[str, Any]:

        return self.log_event(
            event_type="AI_DECISION",

            payment_id=decision.get(
                "payment_id"
            ),

            decision=decision.get(
                "final_action"
            ),

            action=decision.get(
                "final_action"
            ),

            risk_level=decision.get(
                "risk_level"
            ),

            approval_required=decision.get(
                "approval_required"
            ),

            details={
                "amount":
                    decision.get(
                        "amount"
                    ),

                "risk_score":
                    decision.get(
                        "risk_score"
                    ),

                "expected_recovery":
                    decision.get(
                        "expected_recovery"
                    ),

                "recovery_ratio":
                    decision.get(
                        "recovery_ratio"
                    ),

                "decision_reason":
                    decision.get(
                        "decision_reason"
                    ),
            },
        )

    # ========================================================
    # LOG POLICY RESULT
    # ========================================================

    def log_policy_result(
        self,
        decision: Dict[str, Any],
        policy_result: Dict[str, Any],
    ) -> Dict[str, Any]:

        return self.log_event(
            event_type="ACTION_POLICY",

            payment_id=decision.get(
                "payment_id"
            ),

            decision=decision.get(
                "final_action"
            ),

            action=policy_result.get(
                "action"
            ),

            risk_level=decision.get(
                "risk_level"
            ),

            approval_required=policy_result.get(
                "approval_required"
            ),

            execution_mode=policy_result.get(
                "execution_mode"
            ),

            status=(
                "ALLOWED"
                if policy_result.get(
                    "allowed"
                )
                else "BLOCKED"
            ),

            details={
                "policy_reason":
                    policy_result.get(
                        "reason"
                    ),
            },
        )

    # ========================================================
    # LOG ACTION OUTCOME
    # ========================================================

    def log_outcome(
        self,
        payment_id: str,
        action: str,
        status: str,
        details: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:

        return self.log_event(
            event_type="ACTION_OUTCOME",

            payment_id=
                payment_id,

            action=
                action,

            status=
                status,

            details=
                details,
        )

    # ========================================================
    # READ EVENTS
    # ========================================================

    def read_events(
        self,
    ) -> List[Dict[str, Any]]:

        # ----------------------------------------------------
        # PostgreSQL mode
        # ----------------------------------------------------

        if self.database is not None:

            return (
                self.database
                .read_audit_events()
            )

        # ----------------------------------------------------
        # File mode
        # ----------------------------------------------------

        if not self.file_path.exists():

            return []

        events: List[
            Dict[str, Any]
        ] = []

        with self.file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            for line in file:

                line = line.strip()

                if not line:
                    continue

                try:

                    events.append(
                        json.loads(
                            line
                        )
                    )

                except json.JSONDecodeError:

                    continue

        return events