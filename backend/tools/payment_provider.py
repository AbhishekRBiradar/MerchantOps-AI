from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from razorpay.payment_adapter import (
    RazorpayPaymentAdapter,
)


PAYMENTS_FILE = Path(
    "data/payments.csv"
)


class PaymentProvider:
    """
    Unified payment-data provider.

    Supports:
    - Local CSV data
    - Razorpay Test API data
    """

    def __init__(
        self,
        mode: str = "csv",
    ) -> None:

        self.mode = mode.lower().strip()

    def load_csv(
        self,
    ) -> pd.DataFrame:

        if not PAYMENTS_FILE.exists():

            raise FileNotFoundError(
                f"Payment dataset not found: "
                f"{PAYMENTS_FILE}"
            )

        return pd.read_csv(
            PAYMENTS_FILE
        )

    def load_razorpay(
        self,
        count: int = 100,
    ) -> pd.DataFrame:

        adapter = RazorpayPaymentAdapter()

        records = adapter.fetch_payments(
            count=count
        )

        return pd.DataFrame(
            records
        )

    def load(
        self,
        count: int = 100,
    ) -> pd.DataFrame:

        if self.mode == "razorpay":

            return self.load_razorpay(
                count=count
            )

        if self.mode == "csv":

            return self.load_csv()

        raise ValueError(
            "Unsupported payment mode: "
            f"{self.mode}. "
            "Use 'csv' or 'razorpay'."
        )