from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import psycopg
from psycopg.rows import dict_row


class PostgresDatabase:
    """
    PostgreSQL database helper for MerchantOps AI.

    The connection string is read from:
        DATABASE_URL
    """

    def __init__(
        self,
        database_url: Optional[str] = None,
    ) -> None:

        self.database_url = (
            database_url
            or os.getenv("DATABASE_URL")
        )

        if not self.database_url:
            raise ValueError(
                "DATABASE_URL is missing."
            )

    def connect(self):
        return psycopg.connect(
            self.database_url,
            row_factory=dict_row,
        )

    def initialize(self) -> None:
        """
        Create the MerchantOps persistence tables
        if they do not already exist.
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id BIGSERIAL PRIMARY KEY,
                        timestamp TIMESTAMPTZ NOT NULL,
                        event_type TEXT NOT NULL,
                        payment_id TEXT,
                        decision TEXT,
                        action TEXT,
                        risk_level TEXT,
                        approval_required BOOLEAN,
                        execution_mode TEXT,
                        status TEXT NOT NULL,
                        details JSONB NOT NULL DEFAULT '{}'::jsonb
                    );
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_audit_logs_payment_id
                    ON audit_logs(payment_id);
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_audit_logs_event_type
                    ON audit_logs(event_type);
                    """
                )

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS webhook_events (
                        event_id TEXT PRIMARY KEY,
                        event_name TEXT NOT NULL,
                        payment_id TEXT,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
                    );
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_webhook_events_payment_id
                    ON webhook_events(payment_id);
                    """
                )

            connection.commit()

    def insert_audit_event(
        self,
        event: Dict[str, Any],
    ) -> None:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO audit_logs (
                        timestamp,
                        event_type,
                        payment_id,
                        decision,
                        action,
                        risk_level,
                        approval_required,
                        execution_mode,
                        status,
                        details
                    )
                    VALUES (
                        %(timestamp)s,
                        %(event_type)s,
                        %(payment_id)s,
                        %(decision)s,
                        %(action)s,
                        %(risk_level)s,
                        %(approval_required)s,
                        %(execution_mode)s,
                        %(status)s,
                        %(details)s
                    )
                    """,
                    {
                        "timestamp":
                            event["timestamp"],

                        "event_type":
                            event["event_type"],

                        "payment_id":
                            event.get(
                                "payment_id"
                            ),

                        "decision":
                            event.get(
                                "decision"
                            ),

                        "action":
                            event.get(
                                "action"
                            ),

                        "risk_level":
                            event.get(
                                "risk_level"
                            ),

                        "approval_required":
                            event.get(
                                "approval_required"
                            ),

                        "execution_mode":
                            event.get(
                                "execution_mode"
                            ),

                        "status":
                            event["status"],

                        "details":
                            json.dumps(
                                event.get(
                                    "details",
                                    {},
                                )
                            ),
                    },
                )

            connection.commit()

    def read_audit_events(
        self,
    ) -> List[Dict[str, Any]]:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        timestamp,
                        event_type,
                        payment_id,
                        decision,
                        action,
                        risk_level,
                        approval_required,
                        execution_mode,
                        status,
                        details
                    FROM audit_logs
                    ORDER BY id ASC
                    """
                )

                rows = cursor.fetchall()

        events: List[Dict[str, Any]] = []

        for row in rows:

            event = dict(row)

            if event.get("timestamp"):

                event["timestamp"] = (
                    event["timestamp"].isoformat()
                )

            events.append(event)

        return events

    def webhook_exists(
        self,
        event_id: str,
    ) -> bool:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT 1
                    FROM webhook_events
                    WHERE event_id = %s
                    LIMIT 1
                    """,
                    (event_id,),
                )

                return cursor.fetchone() is not None

    def record_webhook(
        self,
        event_id: str,
        event_name: str,
        payment_id: Optional[str] = None,
    ) -> None:

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO webhook_events (
                        event_id,
                        event_name,
                        payment_id
                    )
                    VALUES (
                        %s,
                        %s,
                        %s
                    )
                    ON CONFLICT (
                        event_id
                    )
                    DO NOTHING
                    """,
                    (
                        event_id,
                        event_name,
                        payment_id,
                    ),
                )

            connection.commit()