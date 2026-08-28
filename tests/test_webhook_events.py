from pathlib import Path

from backend.database.webhook_events import (
    WebhookEventStore,
)


def test_event_can_be_recorded(tmp_path: Path):

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


def test_duplicate_event_is_detected(tmp_path: Path):

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