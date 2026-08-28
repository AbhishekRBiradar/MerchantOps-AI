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
                "failure_reason": "bank_error",
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