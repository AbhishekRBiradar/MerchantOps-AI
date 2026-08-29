from __future__ import annotations

import os

from contextlib import contextmanager
from typing import Any, Dict, Iterator, List, Optional

import psycopg


class PostgresDatabase:
    """
    PostgreSQL persistence layer for MerchantOps AI.

    Stores:
        - audit events
        - Razorpay webhook events

    Used in production when DATABASE_URL is configured.
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
                "DATABASE_URL is not configured."
            )

        self._initialized = False

    # ========================================================
    # DATABASE CONNECTION
    # ========================================================

    @contextmanager
    def connection(
        self,
    ) -> Iterator[
        psycopg.Connection
    ]:
        """
        Open a PostgreSQL connection.
        """

        conn = psycopg.connect(
            self.database_url
        )

        try:

            yield conn

            conn.commit()

        except Exception:

            conn.rollback()

            raise

        finally:

            conn.close()

    # ========================================================
    # INITIALIZE DATABASE
    # ========================================================

    def initialize(self) -> None:
        """
        Create required tables and indexes if they do not exist.
        """

        if self._initialized:
            return

        with self.connection() as conn:

            with conn.cursor() as cursor:

                # ------------------------------------------------
                # Audit events
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
                        status TEXT,
                        details JSONB NOT NULL DEFAULT '{}'::jsonb
                    )
                    """
                )

                # ------------------------------------------------
                # Webhook events
                # ------------------------------------------------

                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS webhook_events (
                        event_id TEXT PRIMARY KEY,
                        event_name TEXT NOT NULL,
                        payment_id TEXT,
                        created_at TIMESTAMPTZ NOT NULL
                            DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                # ------------------------------------------------
                # Audit indexes
                # ------------------------------------------------

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_audit_logs_timestamp
                    ON audit_logs(timestamp DESC)
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_audit_logs_event_type
                    ON audit_logs(event_type)
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_audit_logs_payment_id
                    ON audit_logs(payment_id)
                    """
                )

                # ------------------------------------------------
                # Webhook indexes
                # ------------------------------------------------

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_webhook_events_created_at
                    ON webhook_events(created_at DESC)
                    """
                )

                cursor.execute(
                    """
                    CREATE INDEX IF NOT EXISTS
                    idx_webhook_events_payment_id
                    ON webhook_events(payment_id)
                    """
                )

        self._initialized = True

    # ========================================================
    # AUDIT INSERT
    # ========================================================

    def insert_audit_event(
        self,
        event: Dict[str, Any],
    ) -> None:
        """
        Insert one audit event.
        """

        with self.connection() as conn:

            with conn.cursor() as cursor:

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
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        event.get(
                            "timestamp"
                        ),

                        event.get(
                            "event_type"
                        ),

                        event.get(
                            "payment_id"
                        ),

                        event.get(
                            "decision"
                        ),

                        event.get(
                            "action"
                        ),

                        event.get(
                            "risk_level"
                        ),

                        event.get(
                            "approval_required"
                        ),

                        event.get(
                            "execution_mode"
                        ),

                        event.get(
                            "status"
                        ),

                        event.get(
                            "details",
                            {},
                        ),
                    ),
                )

    # ========================================================
    # READ ALL AUDIT EVENTS
    # ========================================================

    def read_audit_events(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Return all audit events, newest first.
        """

        with self.connection() as conn:

            with conn.cursor() as cursor:

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
                    ORDER BY timestamp DESC, id DESC
                    """
                )

                rows = (
                    cursor.fetchall()
                )

        events = []

        for row in rows:

            events.append(
                self._audit_row_to_dict(
                    row
                )
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
        Return the most recent audit events.
        """

        limit = max(
            1,
            min(
                int(limit),
                1000,
            ),
        )

        with self.connection() as conn:

            with conn.cursor() as cursor:

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
                    ORDER BY timestamp DESC, id DESC
                    LIMIT %s
                    """,
                    (
                        limit,
                    ),
                )

                rows = (
                    cursor.fetchall()
                )

        events = []

        for row in rows:

            events.append(
                self._audit_row_to_dict(
                    row
                )
            )

        return events

    # ========================================================
    # AUDIT ROW CONVERSION
    # ========================================================

    @staticmethod
    def _audit_row_to_dict(
        row: Any,
    ) -> Dict[str, Any]:
        """
        Convert PostgreSQL audit row to API dictionary.
        """

        (
            event_id,
            timestamp,
            event_type,
            payment_id,
            decision,
            action,
            risk_level,
            approval_required,
            execution_mode,
            status,
            details,
        ) = row

        return {

            "id":
                event_id,

            "timestamp":
                timestamp.isoformat()
                if hasattr(
                    timestamp,
                    "isoformat",
                )
                else timestamp,

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

    # ========================================================
    # WEBHOOK INSERT
    # ========================================================

    def insert_webhook_event(
        self,
        event_id: str,
        event_name: str,
        payment_id: Optional[str] = None,
    ) -> bool:
        """
        Store a webhook event.

        Returns:
            True  -> inserted
            False -> duplicate
        """

        with self.connection() as conn:

            with conn.cursor() as cursor:

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
                    RETURNING event_id
                    """,
                    (
                        event_id,
                        event_name,
                        payment_id,
                    ),
                )

                row = (
                    cursor.fetchone()
                )

        return row is not None

    # ========================================================
    # WEBHOOK EXISTS
    # ========================================================

    def webhook_event_exists(
        self,
        event_id: str,
    ) -> bool:
        """
        Check whether a webhook event exists.
        """

        with self.connection() as conn:

            with conn.cursor() as cursor:

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
    # READ WEBHOOK EVENTS
    # ========================================================

    def read_webhook_events(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Return stored webhook events, newest first.
        """

        with self.connection() as conn:

            with conn.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        event_id,
                        event_name,
                        payment_id,
                        created_at
                    FROM webhook_events
                    ORDER BY created_at DESC
                    """
                )

                rows = (
                    cursor.fetchall()
                )

        events = []

        for row in rows:

            (
                event_id,
                event_name,
                payment_id,
                created_at,
            ) = row

            events.append(
                {

                    "event_id":
                        event_id,

                    "event_name":
                        event_name,

                    "payment_id":
                        payment_id,

                    "created_at":
                        (
                            created_at.isoformat()
                            if hasattr(
                                created_at,
                                "isoformat",
                            )
                            else created_at
                        ),
                }
            )

        return events

    # ========================================================
    # DATABASE STATS
    # ========================================================

    def get_stats(
        self,
    ) -> Dict[str, int]:
        """
        Return basic table counts.
        """

        with self.connection() as conn:

            with conn.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM audit_logs
                    """
                )

                audit_count = int(
                    cursor.fetchone()[0]
                    or 0
                )

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM webhook_events
                    """
                )

                webhook_count = int(
                    cursor.fetchone()[0]
                    or 0
                )

        return {
            "audit_logs":
                audit_count,

            "webhook_events":
                webhook_count,
        }

    # ========================================================
    # ACTIVITY STATS
    # ========================================================

    def get_activity_stats(
        self,
    ) -> Dict[str, int]:
        """
        Return aggregate MerchantOps activity counts.

        These values are calculated directly by PostgreSQL,
        avoiding dashboard-side counting of only the latest
        audit records.
        """

        with self.connection() as conn:

            with conn.cursor() as cursor:

                # ------------------------------------------------
                # Audit-based counts
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

                (
                    verification_events,
                    verified_payments,
                    webhook_processing,
                ) = cursor.fetchone()

                # ------------------------------------------------
                # Webhook table count
                # ------------------------------------------------

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM webhook_events
                    """
                )

                webhook_events = (
                    cursor.fetchone()[0]
                )

        return {

            "verified_payments":
                int(
                    verified_payments
                    or 0
                ),

            "verification_events":
                int(
                    verification_events
                    or 0
                ),

            "webhook_events":
                int(
                    webhook_events
                    or 0
                ),

            "webhook_processing":
                int(
                    webhook_processing
                    or 0
                ),
        }