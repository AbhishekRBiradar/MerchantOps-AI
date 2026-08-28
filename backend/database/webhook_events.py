from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class WebhookEventStore:
    """
    Simple file-backed idempotency store for webhook events.
    """

    def __init__(
        self,
        path: str = "data/webhook_events.json",
    ) -> None:

        self.path = Path(path)

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.path.exists():
            self.path.write_text(
                "{}",
                encoding="utf-8",
            )

    def _load(self) -> dict[str, Any]:
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

    def exists(
        self,
        event_id: str,
    ) -> bool:
        return event_id in self._load()

    def record(
        self,
        event_id: str,
        event_name: str,
        payment_id: str | None = None,
    ) -> None:

        data = self._load()

        data[event_id] = {
            "event_name": event_name,
            "payment_id": payment_id,
        }

        self._save(data)