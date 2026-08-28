from backend.agents.risk_agent import RiskAgent


def test_low_risk_network_failure():

    agent = RiskAgent()

    candidates = [
        {
            "payment_id": "PAY001",
            "order_id": "ORD001",
            "customer_id": "CUST001",
            "amount": 1000,
            "payment_method": "UPI",
            "failure_reason": "network_error",
            "retry_count": 0,
        }
    ]

    result = agent.evaluate(
        candidates
    )

    assert len(result) == 1
    assert result[0]["risk_level"] == "LOW"
    assert result[0]["recommended_action"] == "RETRY"


def test_high_risk_repeated_insufficient_funds():

    agent = RiskAgent()

    candidates = [
        {
            "payment_id": "PAY002",
            "order_id": "ORD002",
            "customer_id": "CUST002",
            "amount": 7000,
            "payment_method": "CARD",
            "failure_reason": "insufficient_funds",
            "retry_count": 3,
        }
    ]

    result = agent.evaluate(
        candidates
    )

    assert len(result) == 1
    assert result[0]["risk_level"] == "HIGH"
    assert result[0]["recommended_action"] == "DO_NOT_RETRY"