from __future__ import annotations

from typing import Any, Dict

import pandas as pd
from fastapi import FastAPI, HTTPException, Query

from backend.agents.orchestrator import MerchantOpsOrchestrator
from backend.tools.payment_provider import PaymentProvider


# ============================================================
# MERCHANTOPS AI API
# ============================================================

app = FastAPI(
    title="MerchantOps AI",
    description=(
        "AI-powered merchant intelligence, revenue recovery, "
        "risk analysis, simulation, and decision automation."
    ),
    version="1.1.0",
)


# ============================================================
# PAYMENT PROVIDER
# ============================================================

def load_payment_data(
    source: str,
) -> pd.DataFrame:

    source = source.lower().strip()

    if source not in {"csv", "razorpay"}:
        raise ValueError(
            "Invalid source. Use 'csv' or 'razorpay'."
        )

    provider = PaymentProvider(
        mode=source
    )

    return provider.load()


# ============================================================
# MERCHANTOPS PIPELINE
# ============================================================

def run_merchantops(
    source: str,
) -> Dict[str, Any]:

    try:

        payments_df = load_payment_data(
            source
        )

        # Razorpay Test Mode may contain no payments.
        # Return a useful empty result instead of crashing.
        if payments_df.empty:

            return {
                "source": source,
                "operations": {
                    "total_payments": 0,
                    "failed_payments": 0,
                    "captured_payments": 0,
                    "failure_rate": 0.0,
                    "revenue_at_risk": 0.0,
                },
                "recovery_candidates": 0,
                "risk_candidates": 0,
                "simulated_candidates": 0,
                "decisions": 0,
                "action_counts": {
                    "RETRY_NOW": 0,
                    "RETRY_LATER": 0,
                    "REVIEW": 0,
                    "DO_NOTHING": 0,
                },
                "execution_modes": {
                    "MERCHANT_APPROVAL": 0,
                    "SCHEDULED_TEST_ACTION": 0,
                    "BLOCKED": 0,
                    "NO_ACTION": 0,
                },
                "approval_required": 0,
                "allowed_actions": 0,
                "blocked_actions": 0,
                "decision_records": [],
            }

        orchestrator = MerchantOpsOrchestrator(
            payments_df
        )

        result = orchestrator.run()

        result["source"] = source

        return result

    except Exception as exc:

        raise RuntimeError(
            f"MerchantOps pipeline failed: {exc}"
        ) from exc


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root() -> Dict[str, str]:

    return {
        "service": "MerchantOps AI",
        "status": "running",
        "docs": "/docs",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health() -> Dict[str, str]:

    return {
        "status": "healthy",
        "service": "MerchantOps AI",
    }


# ============================================================
# PAYMENTS
# ============================================================

@app.get("/payments")
def payments(
    source: str = Query(
        default="csv",
        description="Payment source: csv or razorpay",
    ),
) -> Dict[str, Any]:

    try:

        df = load_payment_data(
            source
        )

        if df.empty:

            return {
                "source": source,
                "total_payments": 0,
                "failed_payments": 0,
                "captured_payments": 0,
                "failure_rate": 0.0,
                "revenue_at_risk": 0.0,
            }

        status = (
            df["status"]
            .astype(str)
            .str.lower()
            .str.strip()
        )

        failed_mask = (
            status == "failed"
        )

        captured_mask = (
            status == "captured"
        )

        total_payments = len(df)

        failed_payments = int(
            failed_mask.sum()
        )

        captured_payments = int(
            captured_mask.sum()
        )

        revenue_at_risk = float(
            df.loc[
                failed_mask,
                "amount",
            ].sum()
        )

        failure_rate = (
            failed_payments
            / total_payments
            * 100
            if total_payments > 0
            else 0.0
        )

        return {
            "source": source,
            "total_payments":
                total_payments,
            "failed_payments":
                failed_payments,
            "captured_payments":
                captured_payments,
            "failure_rate":
                round(
                    failure_rate,
                    2,
                ),
            "revenue_at_risk":
                round(
                    revenue_at_risk,
                    2,
                ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# ANALYZE
# ============================================================

@app.get("/analyze")
def analyze(
    source: str = Query(
        default="csv",
        description="Payment source: csv or razorpay",
    ),
) -> Dict[str, Any]:

    try:

        return run_merchantops(
            source
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# DECISIONS
# ============================================================

@app.get("/decisions")
def decisions(
    source: str = Query(
        default="csv",
        description="Payment source: csv or razorpay",
    ),
) -> Dict[str, Any]:

    try:

        result = run_merchantops(
            source
        )

        return {
            "source":
                result["source"],

            "count":
                result["decisions"],

            "action_counts":
                result["action_counts"],

            "execution_modes":
                result["execution_modes"],

            "approval_required":
                result["approval_required"],

            "allowed_actions":
                result["allowed_actions"],

            "blocked_actions":
                result["blocked_actions"],

            "decisions":
                result["decision_records"],
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc