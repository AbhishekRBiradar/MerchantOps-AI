from backend.agents.decision_agent import DecisionAgent


def test_low_risk_retry_requires_approval():

    agent = DecisionAgent()

    simulated = [
        {
            "payment_id": "PAY001",
            "amount": 2000,
            "risk_score": 0.20,
            "risk_level": "LOW",
            "recommended_action": "RETRY_NOW",
            "expected_recovery": 1200,
        }
    ]

    result = agent.decide(simulated)

    assert len(result) == 1
    assert result[0]["final_action"] == "RETRY_NOW"
    assert result[0]["approval_required"] is True


def test_high_risk_becomes_do_nothing():

    agent = DecisionAgent()

    simulated = [
        {
            "payment_id": "PAY002",
            "amount": 5000,
            "risk_score": 0.80,
            "risk_level": "HIGH",
            "recommended_action": "RETRY_NOW",
            "expected_recovery": 2000,
        }
    ]

    result = agent.decide(simulated)

    assert len(result) == 1
    assert result[0]["final_action"] == "DO_NOTHING"
    assert result[0]["approval_required"] is False