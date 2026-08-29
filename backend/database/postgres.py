from __future__ import annotations

import os

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

import psycopg

from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


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
            or os.getenv(
                "DATABASE_URL"
            )
        )

        if not self.database_url:

            raise ValueError(
                "DATABASE_URL is missing."
            )

    # ========================================================
    # CONNECTION
    # ========================================================

    def connect(self):
        """
        Create a PostgreSQL connection using dict rows.
        """

        return psycopg.connect(
            self.database_url,
            row_factory=dict_row,
        )

    # ========================================================
    # DATABASE INITIALIZATION
    # ========================================================

    def initialize(self) -> None:
        """
        Create MerchantOps persistence tables and indexes
        when they do not already exist.
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                # ------------------------------------------------
                # AUDIT LOGS
                # ------------------------------------------------

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

                        details JSONB NOT NULL
                            DEFAULT '{}'::jsonb
                    );
                    """
                )

                # ------------------------------------------------
                # AUDIT INDEXES
                # ------------------------------------------------

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
                    CREATE INDEX IF NOT EXISTS
                    idx_audit_logs_timestamp
                    ON audit_logs(timestamp DESC);
                    """
                )

                # ------------------------------------------------
                # WEBHOOK EVENTS
                # ------------------------------------------------

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS webhook_events (
                        event_id TEXT PRIMARY KEY,

                        event_name TEXT NOT NULL,

                        payment_id TEXT,

                        created_at TIMESTAMPTZ NOT NULL
                            DEFAULT NOW()
                    );
                    """
                )

                # ------------------------------------------------
                # WEBHOOK INDEXES
                # ------------------------------------------------

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_webhook_events_payment_id
                    ON webhook_events(payment_id);
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_webhook_events_created_at
                    ON webhook_events(created_at DESC);
                    """
                )

            connection.commit()

    # ========================================================
    # INSERT AUDIT EVENT
    # ========================================================

    def insert_audit_event(
        self,
        event: Dict[str, Any],
    ) -> None:
        """
        Insert one audit event into PostgreSQL.

        `details` is explicitly wrapped with Jsonb so nested
        Python dictionaries/lists are safely adapted to the
        PostgreSQL JSONB column.
        """

        details = event.get(
            "details",
            {},
        )

        if details is None:
            details = {}

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
                            event.get(
                                "timestamp"
                            ),

                        "event_type":
                            event.get(
                                "event_type"
                            ),

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
                            event.get(
                                "status",
                                "RECORDED",
                            ),

                        "details":
                            Jsonb(details),
                    },
                )

            connection.commit()

    # ========================================================
    # READ ALL AUDIT EVENTS
    # ========================================================

    def read_audit_events(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Return all audit events in ascending database order.
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
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

        events: List[
            Dict[str, Any]
        ] = []

        for row in rows:

            event = dict(row)

            if event.get(
                "timestamp"
            ):

                event["timestamp"] = (
                    event[
                        "timestamp"
                    ].isoformat()
                )

            events.append(
                event
            )

        return events

    # ========================================================
    # READ RECENT AUDIT EVENTS
    # ========================================================

    def read_recent_audit_events(
        self,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Return the newest audit events first.
        """

        limit = max(
            1,
            min(
                int(limit),
                1000,
            ),
        )

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
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
                    ORDER BY
                        timestamp DESC,
                        id DESC
                    LIMIT %s
                    """,
                    (
                        limit,
                    ),
                )

                rows = cursor.fetchall()

        events: List[
            Dict[str, Any]
        ] = []

        for row in rows:

            event = dict(row)

            if event.get(
                "timestamp"
            ):

                event["timestamp"] = (
                    event[
                        "timestamp"
                    ].isoformat()
                )

            events.append(
                event
            )

        return events

    # ========================================================
    # WEBHOOK EXISTS
    # ========================================================

    def webhook_exists(
        self,
        event_id: str,
    ) -> bool:
        """
        Return True when a webhook event already exists.
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT 1
                    FROM webhook_events
                    WHERE event_id = %s
                    LIMIT 1
                    """,
                    (
                        event_id,
                    ),
                )

                return (
                    cursor.fetchone()
                    is not None
                )

    # ========================================================
    # RECORD WEBHOOK
    # ========================================================

    def record_webhook(
        self,
        event_id: str,
        event_name: str,
        payment_id: Optional[str] = None,
    ) -> None:
        """
        Record a webhook event.

        Duplicate event IDs are ignored.
        """

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

    # ========================================================
    # READ WEBHOOK EVENTS
    # ========================================================

    def read_webhook_events(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Return all stored webhook events, newest first.
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        event_id,
                        event_name,
                        payment_id,
                        created_at
                    FROM webhook_events
                    ORDER BY
                        created_at DESC
                    """
                )

                rows = cursor.fetchall()

        events: List[
            Dict[str, Any]
        ] = []

        for row in rows:

            event = dict(row)

            if event.get(
                "created_at"
            ):

                event["created_at"] = (
                    event[
                        "created_at"
                    ].isoformat()
                )

            events.append(
                event
            )

        return events

    # ========================================================
    # DATABASE STATS
    # ========================================================

    def get_stats(
        self,
    ) -> Dict[str, int]:
        """
        Return basic PostgreSQL record counts.
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM audit_logs
                    """
                )

                audit_logs = int(
                    cursor.fetchone()[
                        0
                    ]
                    or 0
                )

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM webhook_events
                    """
                )

                webhook_events = int(
                    cursor.fetchone()[
                        0
                    ]
                    or 0
                )

        return {

            "audit_logs":
                audit_logs,

            "webhook_events":
                webhook_events,
        }

    # ========================================================
    # ACTIVITY STATISTICS
    # ========================================================

    def get_activity_stats(
        self,
    ) -> Dict[str, int]:
        """
        Return authoritative activity counts directly from
        PostgreSQL.

        This avoids counting only the latest 1000 audit rows
        inside the Streamlit dashboard.
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                # ------------------------------------------------
                # AUDIT COUNTS
                # ------------------------------------------------

                cursor.execute(
                    """
                    SELECT
                        COUNT(*) FILTER (
                            WHERE event_type =
                            'PAYMENT_VERIFICATION'
                        ) AS verification_events,

                        COUNT(*) FILTER (
                            WHERE event_type =
                            'PAYMENT_VERIFICATION'
                            AND status =
                            'VERIFIED'
                        ) AS verified_payments,

                        COUNT(*) FILTER (
                            WHERE event_type =
                            'WEBHOOK_PROCESSING'
                        ) AS webhook_processing

                    FROM audit_logs
                    """
                )

                row = cursor.fetchone()

                verification_events = int(
                    row[0]
                    or 0
                )

                verified_payments = int(
                    row[1]
                    or 0
                )

                webhook_processing = int(
                    row[2]
                    or 0
                )

                # ------------------------------------------------
                # WEBHOOK EVENT COUNT
                # ------------------------------------------------

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM webhook_events
                    """
                )

                webhook_events = int(
                    cursor.fetchone()[
                        0
                    ]
                    or 0
                )

        return {

            "verified_payments":
                verified_payments,

            "verification_events":
                verification_events,

            "webhook_events":
                webhook_events,

            "webhook_processing":
                webhook_processing,
        }

    # ========================================================
    # COMPATIBILITY ALIAS
    # ========================================================

    def insert_webhook_event(
        self,
        event_id: str,
        event_name: str,
        payment_id: Optional[str] = None,
    ) -> None:
        """
        Compatibility alias for webhook persistence.
        """

        self.record_webhook(
            event_id=event_id,
            event_name=event_name,
            payment_id=payment_id,
        )

    # ========================================================
    # COMPATIBILITY ALIAS
    # ========================================================

    def webhook_event_exists(
        self,
        event_id: str,
    ) -> bool:
        """
        Compatibility alias for webhook existence checks.
        """

        return self.webhook_exists(
            event_id
        )