from pathlib import Path

from backend.database.webhook_events import (
    WebhookEventStore,
)


class FakeDatabase:
    """
    Small in-memory database replacement used only for tests.
    """

    def __init__(self):

        self.events = {}

    def webhook_exists(
        self,
        event_id: str,
    ) -> bool:

        return event_id in self.events

    def record_webhook(
        self,
        event_id: str,
        event_name: str,
        payment_id: str | None = None,
    ) -> None:

        self.events.setdefault(
            event_id,
            {
                "event_name": event_name,
                "payment_id": payment_id,
            },
        )


# ============================================================
# FILE-BASED STORE TESTS
# ============================================================

def test_event_can_be_recorded(
    tmp_path: Path,
):

    store = WebhookEventStore(
        str(
            tmp_path / "events.json"
        )
    )

    assert (
        store.exists("evt_001")
        is False
    )

    store.record(
        event_id="evt_001",
        event_name="payment.failed",
        payment_id="pay_001",
    )

    assert (
        store.exists("evt_001")
        is True
    )


def test_duplicate_event_is_detected(
    tmp_path: Path,
):

    store = WebhookEventStore(
        str(
            tmp_path / "events.json"
        )
    )

    store.record(
        event_id="evt_002",
        event_name="payment.captured",
        payment_id="pay_002",
    )

    assert (
        store.exists("evt_002")
        is True
    )


# ============================================================
# POSTGRES-BACKED STORE BEHAVIOR
# ============================================================

def test_database_event_can_be_recorded():

    database = FakeDatabase()

    store = WebhookEventStore(
        database=database
    )

    assert (
        store.exists("evt_db_001")
        is False
    )

    store.record(
        event_id="evt_db_001",
        event_name="payment.failed",
        payment_id="pay_db_001",
    )

    assert (
        store.exists("evt_db_001")
        is True
    )


def test_database_duplicate_event_is_detected():

    database = FakeDatabase()

    store = WebhookEventStore(
        database=database
    )

    store.record(
        event_id="evt_db_002",
        event_name="payment.captured",
        payment_id="pay_db_002",
    )

    assert (
        store.exists("evt_db_002")
        is True
    )

    # Record the same event again.
    store.record(
        event_id="evt_db_002",
        event_name="payment.captured",
        payment_id="pay_db_002",
    )

    # Only one database record should exist.
    assert (
        len(database.events)
        == 1
    )