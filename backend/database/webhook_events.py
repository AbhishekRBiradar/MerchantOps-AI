from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Optional

from backend.database.postgres import (
    PostgresDatabase,
)


class WebhookEventStore:
    """
    Idempotency store.

    Local development:
        data/webhook_events.json

    Production:
        PostgreSQL webhook_events table
    """

    def __init__(
        self,
        path: str = (
            "data/webhook_events.json"
        ),
        database: Optional[
            PostgresDatabase
        ] = None,
    ) -> None:

        self.path = Path(path)

        self.database = database

        database_url = os.getenv(
            "DATABASE_URL"
        )

        # ----------------------------------------------------
        # PostgreSQL mode
        # ----------------------------------------------------

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

            return

        # ----------------------------------------------------
        # Local file mode
        # ----------------------------------------------------

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.path.exists():

            self.path.write_text(
                "{}",
                encoding="utf-8",
            )

    # ========================================================
    # LOCAL FILE HELPERS
    # ========================================================

    def _load(
        self,
    ) -> dict[str, Any]:

        try:

            return json.loads(
                self.path.read_text(
                    encoding="utf-8"
                )
            )

        except (
            json.JSONDecodeError,
            OSError,
        ):

            return {}

    def _save(
        self,
        data: dict[str, Any],
    ) -> None:

        self.path.write_text(
            json.dumps(
                data,
                indent=2,
            ),
            encoding="utf-8",
        )

    # ========================================================
    # CHECK EXISTENCE
    # ========================================================

    def exists(
        self,
        event_id: str,
    ) -> bool:

        if self.database is not None:

            return (
                self.database
                .webhook_exists(
                    event_id
                )
            )

        return (
            event_id
            in self._load()
        )

    # ========================================================
    # RECORD EVENT
    # ========================================================

    def record(
        self,
        event_id: str,
        event_name: str,
        payment_id: str | None = None,
    ) -> None:

        if self.database is not None:

            self.database.record_webhook(
                event_id=
                    event_id,

                event_name=
                    event_name,

                payment_id=
                    payment_id,
            )

            return

        data = self._load()

        data[event_id] = {
            "event_name":
                event_name,

            "payment_id":
                payment_id,
        }

        self._save(data)