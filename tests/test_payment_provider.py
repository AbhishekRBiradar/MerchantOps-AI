import pandas as pd

from backend.tools.payment_provider import (
    PaymentProvider,
)


def test_csv_provider():

    provider = PaymentProvider(
        mode="csv"
    )

    df = provider.load()

    assert isinstance(
        df,
        pd.DataFrame,
    )

    assert len(df) > 0

    assert "payment_id" in df.columns


def test_razorpay_provider_with_mock():

    provider = PaymentProvider(
        mode="razorpay"
    )

    provider.load_razorpay = (
        lambda count=100:
        pd.DataFrame(
            [
                {
                    "payment_id":
                        "pay_test_001",

                    "amount":
                        2500.0,

                    "payment_method":
                        "UPI",

                    "status":
                        "failed",

                    "failure_reason":
                        "network_error",

                    "retry_count":
                        0,
                }
            ]
        )
    )

    df = provider.load()

    assert len(df) == 1

    assert (
        df.iloc[0]["payment_id"]
        == "pay_test_001"
    )

    assert (
        df.iloc[0]["amount"]
        == 2500.0
    )