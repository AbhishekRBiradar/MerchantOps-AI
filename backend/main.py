from __future__ import annotations

from typing import Any, Dict

import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.agents.orchestrator import MerchantOpsOrchestrator
from backend.tools.payment_provider import PaymentProvider
from razorpay.client import RazorpayClient


# ============================================================
# MERCHANTOPS AI API
# ============================================================

app = FastAPI(
    title="MerchantOps AI",
    description=(
        "AI-powered merchant intelligence, revenue recovery, "
        "risk analysis, simulation, and decision automation."
    ),
    version="1.2.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://127.0.0.1:8501",
        "http://localhost:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# PAYMENT DATA
# ============================================================

def load_payment_data(
    source: str,
) -> pd.DataFrame:
    """
    Load payment data from the selected source.

    Supported:
        csv
        razorpay
    """

    source = (
        source
        .lower()
        .strip()
    )

    if source not in {
        "csv",
        "razorpay",
    }:
        raise ValueError(
            "Invalid payment source. "
            "Use 'csv' or 'razorpay'."
        )

    provider = PaymentProvider(
        mode=source
    )

    return provider.load()


# ============================================================
# EMPTY RESULT
# ============================================================

def empty_analysis(
    source: str,
) -> Dict[str, Any]:
    """
    Return a valid empty MerchantOps result.

    Useful when Razorpay Test Mode contains
    no payments.
    """

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


# ============================================================
# RUN MERCHANTOPS
# ============================================================

def run_merchantops(
    source: str,
) -> Dict[str, Any]:
    """
    Execute the complete MerchantOps AI pipeline.
    """

    try:

        payments_df = load_payment_data(
            source
        )

        if payments_df.empty:

            return empty_analysis(
                source
            )

        orchestrator = (
            MerchantOpsOrchestrator(
                payments_df
            )
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
    """
    API root endpoint.
    """

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
    """
    Health check.
    """

    return {
        "status": "healthy",
        "service": "MerchantOps AI",
    }


# ============================================================
# CREATE RAZORPAY ORDER
# ============================================================

@app.post(
    "/razorpay/create-order"
)
def create_razorpay_order(
    amount: int = Query(
        default=50000,
        description=(
            "Amount in paise. "
            "₹500 = 50000."
        ),
    ),
) -> Dict[str, Any]:
    """
    Create a Razorpay Test Mode order.
    """

    try:

        if amount <= 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Amount must be greater than zero."
                ),
            )

        client = RazorpayClient()

        order = client.create_order(
            amount=amount,
            currency="INR",
            receipt=(
                "merchantops_test_order"
            ),
        )

        return {
            "order_id":
                order["id"],

            "amount":
                order["amount"],

            "currency":
                order["currency"],

            "status":
                order["status"],
        }

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# PAYMENTS
# ============================================================

@app.get("/payments")
def payments(
    source: str = Query(
        default="csv",
        description=(
            "Payment source: "
            "csv or razorpay"
        ),
    ),
) -> Dict[str, Any]:
    """
    Return payment statistics.
    """

    try:

        df = load_payment_data(
            source
        )

        # ----------------------------------------------------
        # Empty data source
        # ----------------------------------------------------

        if df.empty:

            return {
                "source": source,
                "total_payments": 0,
                "failed_payments": 0,
                "captured_payments": 0,
                "failure_rate": 0.0,
                "revenue_at_risk": 0.0,
            }

        # ----------------------------------------------------
        # Normalize status
        # ----------------------------------------------------

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
        description=(
            "Payment source: "
            "csv or razorpay"
        ),
    ),
) -> Dict[str, Any]:
    """
    Run the complete MerchantOps AI analysis.
    """

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
        description=(
            "Payment source: "
            "csv or razorpay"
        ),
    ),
) -> Dict[str, Any]:
    """
    Return final AI decisions.
    """

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