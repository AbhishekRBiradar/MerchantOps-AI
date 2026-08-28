from backend.tools.action_tools import evaluate_action


def test_high_risk_action_is_blocked():

    decision = {
        "final_action": "RETRY_NOW",
        "risk_level": "HIGH",
        "risk_score": 0.85,
        "amount": 1000,
    }

    result = evaluate_action(
        decision
    )

    assert result["allowed"] is False
    assert result["execution_mode"] == "BLOCKED"


def test_retry_now_requires_approval():

    decision = {
        "final_action": "RETRY_NOW",
        "risk_level": "LOW",
        "risk_score": 0.20,
        "amount": 1000,
    }

    result = evaluate_action(
        decision
    )

    assert result["allowed"] is True
    assert result["approval_required"] is True
    assert (
        result["execution_mode"]
        == "MERCHANT_APPROVAL"
    )


def test_retry_later_is_bounded():

    decision = {
        "final_action": "RETRY_LATER",
        "risk_level": "LOW",
        "risk_score": 0.20,
        "amount": 1000,
    }

    result = evaluate_action(
        decision
    )

    assert result["allowed"] is True
    assert result["approval_required"] is False
    assert (
        result["execution_mode"]
        == "SCHEDULED_TEST_ACTION"
    )