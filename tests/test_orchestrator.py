import pandas as pd

from backend.agents.orchestrator import (
    MerchantOpsOrchestrator,
)


def test_orchestrator_pipeline():

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
                "created_at": "2026-08-01T11:00:00",
                "retry_count": 0,
            },
        ]
    )

    orchestrator = MerchantOpsOrchestrator(
        df
    )

    result = orchestrator.run()

    assert (
        result["operations"][
            "total_payments"
        ] == 2
    )

    assert (
        result["operations"][
            "failed_payments"
        ] == 1
    )

    assert (
        result["operations"][
            "revenue_at_risk"
        ] == 1000.0
    )

    assert (
        result["recovery_candidates"]
        == 1
    )

    assert sum(
        result["action_counts"].values()
    ) == 1

    assert len(
        result["decisions"]
    ) == 1