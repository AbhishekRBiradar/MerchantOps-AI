import pandas as pd

from backend.agents.revenue_agent import RevenueAgent


def test_revenue_agent():

    df = pd.DataFrame(
        [
            {
                "payment_id": "PAY001",
                "order_id": "ORD001",
                "customer_id": "CUST001",
                "amount": 1000,
                "payment_method": "UPI",
                "status": "failed",
                "failure_reason": "network_error",
                "error_code": "TEST_ERROR",
                "error_description": "Network failure",
                "error_source": "gateway",
                "error_step": "payment_initiation",
                "created_at": "2026-08-01T10:00:00",
                "retry_count": 0,
            },
            {
                "payment_id": "PAY002",
                "order_id": "ORD002",
                "customer_id": "CUST002",
                "amount": 2000,
                "payment_method": "CARD",
                "status": "captured",
                "failure_reason": "",
                "error_code": None,
                "error_description": None,
                "error_source": None,
                "error_step": None,
                "created_at": "2026-08-01T11:00:00",
                "retry_count": 0,
            },
        ]
    )

    agent = RevenueAgent(df)

    result = agent.analyze()

    assert result["total_payments"] == 2
    assert result["failed_payments"] == 1
    assert result["captured_payments"] == 1
    assert result["revenue_at_risk"] == 1000.0

    candidate = result[
        "recovery_candidates"
    ][0]

    assert (
        candidate["payment_id"]
        == "PAY001"
    )

    assert (
        candidate["error_code"]
        == "TEST_ERROR"
    )

    assert (
        candidate["error_source"]
        == "gateway"
    )

    assert (
        candidate["error_step"]
        == "payment_initiation"
    )