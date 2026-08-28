from __future__ import annotations

from pathlib import Path
from typing import List, Dict, Any

import pandas as pd


PAYMENTS_FILE = Path("data/payments.csv")


def load_payments(
    file_path: Path = PAYMENTS_FILE,
) -> pd.DataFrame:
    """Load merchant payment events from CSV."""

    if not file_path.exists():
        raise FileNotFoundError(
            f"Payment dataset not found: {file_path}"
        )

    df = pd.read_csv(file_path)

    required_columns = {
        "payment_id",
        "order_id",
        "customer_id",
        "amount",
        "payment_method",
        "status",
        "failure_reason",
        "created_at",
        "retry_count",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing payment columns: {sorted(missing)}"
        )

    df["amount"] = pd.to_numeric(
        df["amount"],
        errors="coerce",
    ).fillna(0)

    df["retry_count"] = pd.to_numeric(
        df["retry_count"],
        errors="coerce",
    ).fillna(0).astype(int)

    df["status"] = (
        df["status"]
        .astype(str)
        .str.lower()
        .str.strip()
    )

    df["payment_method"] = (
        df["payment_method"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    return df


def get_failed_payments(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Return failed payment events."""

    return df[
        df["status"] == "failed"
    ].copy()


def get_captured_payments(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Return successful payment events."""

    return df[
        df["status"] == "captured"
    ].copy()


def get_revenue_at_risk(
    df: pd.DataFrame,
) -> float:
    """Calculate total value of failed payments."""

    failed = get_failed_payments(df)

    return float(
        failed["amount"].sum()
    )


def get_failure_rate(
    df: pd.DataFrame,
) -> float:
    """Calculate payment failure percentage."""

    if df.empty:
        return 0.0

    failed = len(
        get_failed_payments(df)
    )

    return (
        failed / len(df) * 100
    )


def get_top_failed_payments(
    df: pd.DataFrame,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Return the highest-value failed payments."""

    failed = get_failed_payments(df)

    failed = failed.sort_values(
        by="amount",
        ascending=False,
    ).head(limit)

    return failed[
        [
            "payment_id",
            "order_id",
            "customer_id",
            "amount",
            "payment_method",
            "failure_reason",
            "retry_count",
            "created_at",
        ]
    ].to_dict(
        orient="records"
    )


def get_failure_summary(
    df: pd.DataFrame,
) -> Dict[str, Any]:
    """Return a compact payment health summary."""

    failed = get_failed_payments(df)
    captured = get_captured_payments(df)

    return {
        "total_payments": int(len(df)),
        "failed_payments": int(len(failed)),
        "captured_payments": int(len(captured)),
        "failure_rate": round(
            get_failure_rate(df),
            2,
        ),
        "revenue_at_risk": round(
            get_revenue_at_risk(df),
            2,
        ),
    }