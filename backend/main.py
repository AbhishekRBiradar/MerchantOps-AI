from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd
from fastapi import FastAPI, HTTPException

from backend.agents.orchestrator import MerchantOpsOrchestrator


# ============================================================
# MERCHANTOPS AI API
# ============================================================

app = FastAPI(
    title="MerchantOps AI",
    description=(
        "AI-powered merchant intelligence, "
        "revenue recovery, risk analysis, "
        "simulation, and decision automation platform."
    ),
    version="1.0.0",
)


# ============================================================
# DATA CONFIGURATION
# ============================================================

PAYMENTS_FILE = Path(
    "data/payments.csv"
)


# ============================================================
# DATA LOADER
# ============================================================

def load_payments() -> pd.DataFrame:
    """
    Load merchant payment events.
    """

    if not PAYMENTS_FILE.exists():

        raise FileNotFoundError(
            f"Payment dataset not found: "
            f"{PAYMENTS_FILE}"
        )

    return pd.read_csv(
        PAYMENTS_FILE
    )


# ============================================================
# MERCHANTOPS PIPELINE
# ============================================================

def run_merchantops() -> Dict[str, Any]:
    """
    Run the complete MerchantOps AI pipeline.
    """

    try:

        payments_df = load_payments()

        orchestrator = (
            MerchantOpsOrchestrator(
                payments_df
            )
        )

        return orchestrator.run()

    except Exception as exc:

        raise RuntimeError(
            f"MerchantOps pipeline failed: {exc}"
        ) from exc


# ============================================================
# ROOT ENDPOINT
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
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health() -> Dict[str, str]:
    """
    Health check endpoint.
    """

    return {
        "status": "healthy",
        "service": "MerchantOps AI",
    }


# ============================================================
# PAYMENTS ENDPOINT
# ============================================================

@app.get("/payments")
def payments() -> Dict[str, Any]:
    """
    Return payment statistics.
    """

    try:

        df = load_payments()

        total_payments = len(df)

        failed_mask = (
            df["status"]
            .astype(str)
            .str.lower()
            .str.strip()
            == "failed"
        )

        captured_mask = (
            df["status"]
            .astype(str)
            .str.lower()
            .str.strip()
            == "captured"
        )

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
# ANALYZE ENDPOINT
# ============================================================

@app.get("/analyze")
def analyze() -> Dict[str, Any]:
    """
    Run complete MerchantOps AI analysis.
    """

    try:

        return run_merchantops()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# DECISIONS ENDPOINT
# ============================================================

@app.get("/decisions")
def decisions() -> Dict[str, Any]:
    """
    Return final AI decisions.
    """

    try:

        result = run_merchantops()

        return {
            "count":
                result["decisions"],

            "action_counts":
                result["action_counts"],

            "execution_modes":
                result[
                    "execution_modes"
                ],

            "approval_required":
                result[
                    "approval_required"
                ],

            "allowed_actions":
                result[
                    "allowed_actions"
                ],

            "blocked_actions":
                result[
                    "blocked_actions"
                ],

            "decisions":
                result[
                    "decision_records"
                ],
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc