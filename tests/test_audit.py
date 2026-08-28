from pathlib import Path

from backend.database.audit import AuditLogger


def test_audit_logger_records_event(
    tmp_path: Path,
):

    audit_file = (
        tmp_path
        / "audit_log.jsonl"
    )

    logger = AuditLogger(
        audit_file
    )

    event = logger.log_event(
        event_type="TEST_EVENT",
        payment_id="PAY001",
        decision="RETRY_NOW",
        action="RETRY_NOW",
        risk_level="LOW",
        approval_required=True,
        execution_mode="MERCHANT_APPROVAL",
        details={
            "amount": 1000
        },
    )

    assert (
        event["event_type"]
        == "TEST_EVENT"
    )

    events = logger.read_events()

    assert len(events) == 1

    assert (
        events[0]["payment_id"]
        == "PAY001"
    )


def test_decision_and_policy_audit(
    tmp_path: Path,
):

    audit_file = (
        tmp_path
        / "audit_log.jsonl"
    )

    logger = AuditLogger(
        audit_file
    )

    decision = {
        "payment_id": "PAY002",
        "amount": 2000,
        "risk_score": 0.20,
        "risk_level": "LOW",
        "final_action": "RETRY_NOW",
        "approval_required": True,
        "expected_recovery": 1200,
        "recovery_ratio": 0.60,
        "decision_reason":
            "Recovery opportunity exists.",
    }

    policy = {
        "allowed": True,
        "approval_required": True,
        "execution_mode":
            "MERCHANT_APPROVAL",
        "action":
            "RETRY_NOW",
        "reason":
            "Merchant approval required.",
    }

    logger.log_decision(
        decision
    )

    logger.log_policy_result(
        decision,
        policy,
    )

    events = logger.read_events()

    assert len(events) == 2

    assert (
        events[0]["event_type"]
        == "AI_DECISION"
    )

    assert (
        events[1]["event_type"]
        == "ACTION_POLICY"
    )