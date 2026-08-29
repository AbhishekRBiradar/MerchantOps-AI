from __future__ import annotations

import json
import os

from typing import (
    Any,
    Dict,
    List,
    Optional,
)

import psycopg

from psycopg.rows import dict_row


class PostgresDatabase:
    """
    PostgreSQL database helper for MerchantOps AI.

    The connection string is read from:

        DATABASE_URL

    Production:
        PostgreSQL

    Local development:
        This class is only used when DATABASE_URL exists.
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

        return psycopg.connect(
            self.database_url,
            row_factory=dict_row,
        )

    # ========================================================
    # INITIALIZE DATABASE
    # ========================================================

    def initialize(
        self,
    ) -> None:
        """
        Create required MerchantOps tables and indexes
        if they do not already exist.
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                # ------------------------------------------------
                # Audit table
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
                # Audit indexes
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
                    ON audit_logs(timestamp);
                    """
                )

                # ------------------------------------------------
                # Webhook event table
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
                # Webhook indexes
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
                    ON webhook_events(created_at);
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
        """

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
                            event[
                                "timestamp"
                            ],

                        "event_type":
                            event[
                                "event_type"
                            ],

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
                            event[
                                "status"
                            ],

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

    # ========================================================
    # READ AUDIT EVENTS
    # ========================================================

    def read_audit_events(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Read all audit events in chronological order.
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

            # ----------------------------------------------------
            # Convert database timestamp to JSON-safe string
            # ----------------------------------------------------

            if event.get(
                "timestamp"
            ):

                event[
                    "timestamp"
                ] = (
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
        Read the most recent audit events.

        Newest events are returned first.
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
                    ORDER BY id DESC
                    LIMIT %s
                    """,
                    (limit,),
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

                event[
                    "timestamp"
                ] = (
                    event[
                        "timestamp"
                    ].isoformat()
                )

            events.append(
                event
            )

        return events

    # ========================================================
    # CHECK WEBHOOK EXISTENCE
    # ========================================================

    def webhook_exists(
        self,
        event_id: str,
    ) -> bool:
        """
        Check whether a Razorpay event ID has already
        been processed.
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
                    (event_id,),
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
        Record a processed webhook event.

        event_id is the PRIMARY KEY, so duplicates cannot
        create another record.
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
        Read all stored Razorpay webhook events.
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
                    ORDER BY created_at ASC
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

                event[
                    "created_at"
                ] = (
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
        Return basic database record counts.
        """

        with self.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        (
                            SELECT COUNT(*)
                            FROM audit_logs
                        ) AS audit_logs,

                        (
                            SELECT COUNT(*)
                            FROM webhook_events
                        ) AS webhook_events
                    """
                )

                row = (
                    cursor.fetchone()
                )

        return {
            "audit_logs":
                int(
                    row[
                        "audit_logs"
                    ]
                ),

            "webhook_events":
                int(
                    row[
                        "webhook_events"
                    ]
                ),
        }