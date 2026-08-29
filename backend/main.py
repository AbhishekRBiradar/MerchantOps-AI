from __future__ import annotations

import json
import os
from typing import Any, Dict

import pandas as pd
from dotenv import load_dotenv
from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    Request,
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.orchestrator import (
    MerchantOpsOrchestrator,
)
from backend.database.audit import (
    AuditLogger,
)
from backend.database.postgres import (
    PostgresDatabase,
)
from backend.database.webhook_events import (
    WebhookEventStore,
)
from backend.tools.payment_provider import (
    PaymentProvider,
)
from backend.tools.webhook_processor import (
    RazorpayWebhookProcessor,
)

from razorpay.client import (
    RazorpayClient,
)
from razorpay.webhook import (
    RazorpayWebhookVerifier,
)


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# MERCHANTOPS AI API
# ============================================================

app = FastAPI(
    title="MerchantOps AI",
    description=(
        "AI-powered merchant intelligence, revenue recovery, "
        "risk analysis, simulation, decision automation, "
        "payment verification, webhook processing, and "
        "governed payment operations."
    ),
    version="1.8.0",
)


# ============================================================
# ENVIRONMENT CONFIGURATION
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        (
            "http://127.0.0.1:5500,"
            "http://localhost:5500,"
            "http://127.0.0.1:8501,"
            "http://localhost:8501"
        ),
    ).split(",")
    if origin.strip()
]


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class PaymentVerificationRequest(
    BaseModel
):
    """
    Razorpay Checkout verification payload.
    """

    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


# ============================================================
# CONFIGURATION
# ============================================================

audit_logger = (
    AuditLogger()
)

webhook_processor = (
    RazorpayWebhookProcessor(
        audit_logger=audit_logger
    )
)

webhook_event_store = (
    WebhookEventStore()
)


# ============================================================
# PAYMENT DATA
# ============================================================

def load_payment_data(
    source: str,
) -> pd.DataFrame:
    """
    Load payment data from the selected provider.

    Supported sources:
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

    provider = (
        PaymentProvider(
            mode=source
        )
    )

    return provider.load()


# ============================================================
# EMPTY ANALYSIS
# ============================================================

def empty_analysis(
    source: str,
) -> Dict[str, Any]:
    """
    Return an empty MerchantOps analysis.
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

        payments_df = (
            load_payment_data(
                source
            )
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

        result = (
            orchestrator.run()
        )

        result["source"] = (
            source
        )

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
        "service":
            "MerchantOps AI",

        "status":
            "running",

        "docs":
            "/docs",

        "webhook":
            "/webhooks/razorpay",

        "payment_verification":
            "/razorpay/verify-payment",

        "api_url":
            API_URL,

        "database_health":
            "/health/database",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health() -> Dict[str, str]:
    """
    API health check.
    """

    return {
        "status":
            "healthy",

        "service":
            "MerchantOps AI",
    }


# ============================================================
# DATABASE HEALTH
# ============================================================

@app.get(
    "/health/database"
)
def database_health() -> Dict[str, Any]:
    """
    Check whether the production PostgreSQL database
    is configured, reachable, and contains the required
    MerchantOps tables.
    """

    try:

        database_url = os.getenv(
            "DATABASE_URL"
        )

        # ----------------------------------------------------
        # Local development fallback
        # ----------------------------------------------------

        if not database_url:

            return {
                "api":
                    "healthy",

                "database":
                    "not_configured",

                "message":
                    (
                        "DATABASE_URL is not configured. "
                        "Local file-based persistence is active."
                    ),
            }

        # ----------------------------------------------------
        # Connect to PostgreSQL
        # ----------------------------------------------------

        database = (
            PostgresDatabase(
                database_url
            )
        )

        # ----------------------------------------------------
        # Ensure tables exist
        # ----------------------------------------------------

        database.initialize()

        # ----------------------------------------------------
        # Test connection and count records
        # ----------------------------------------------------

        with database.connect() as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        (
                            SELECT COUNT(*)
                            FROM audit_logs
                        ) AS audit_logs,

                        (
                            SELECT COUNT(*)
                            FROM webhook_events
                        ) AS webhook_events
                    """
                )

                row = (
                    cursor.fetchone()
                )

        return {
            "api":
                "healthy",

            "database":
                "healthy",

            "audit_logs":
                int(
                    row["audit_logs"]
                ),

            "webhook_events":
                int(
                    row["webhook_events"]
                ),
        }

    except Exception as exc:

        return {
            "api":
                "healthy",

            "database":
                "unhealthy",

            "error":
                str(exc),
        }


# ============================================================
# RAZORPAY CREATE ORDER
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

        client = (
            RazorpayClient()
        )

        order = (
            client.create_order(
                amount=amount,
                currency="INR",
                receipt=(
                    "merchantops_test_order"
                ),
            )
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
# RAZORPAY PAYMENT VERIFICATION
# ============================================================

@app.post(
    "/razorpay/verify-payment"
)
def verify_razorpay_payment(
    payload: PaymentVerificationRequest,
) -> Dict[str, Any]:
    """
    Verify the Razorpay Checkout payment signature.

    After successful verification, fetch the payment
    directly from Razorpay and return trusted details.
    """

    try:

        client = (
            RazorpayClient()
        )

        # ----------------------------------------------------
        # 1. Verify Checkout signature
        # ----------------------------------------------------

        verified = (
            client.verify_payment_signature(
                order_id=(
                    payload.razorpay_order_id
                ),

                payment_id=(
                    payload.razorpay_payment_id
                ),

                signature=(
                    payload.razorpay_signature
                ),
            )
        )

        # ----------------------------------------------------
        # 2. Reject invalid signature
        # ----------------------------------------------------

        if not verified:

            audit_logger.log_event(
                event_type=(
                    "PAYMENT_VERIFICATION"
                ),

                payment_id=(
                    payload.razorpay_payment_id
                ),

                action=(
                    "VERIFY_PAYMENT"
                ),

                status=(
                    "REJECTED"
                ),

                details={
                    "order_id":
                        payload.razorpay_order_id,

                    "reason":
                        (
                            "Invalid Razorpay "
                            "payment signature."
                        ),
                },
            )

            return {
                "verified":
                    False,

                "status":
                    "rejected",

                "payment_id":
                    payload.razorpay_payment_id,

                "order_id":
                    payload.razorpay_order_id,

                "reason":
                    (
                        "Invalid Razorpay "
                        "payment signature."
                    ),
            }

        # ----------------------------------------------------
        # 3. Fetch payment directly from Razorpay
        # ----------------------------------------------------

        payment = (
            client.fetch_payment(
                payload.razorpay_payment_id
            )
        )

        # ----------------------------------------------------
        # 4. Extract trusted payment values
        # ----------------------------------------------------

        amount_paise = (
            payment.get(
                "amount"
            )
        )

        amount_rupees = (
            float(amount_paise) / 100
            if amount_paise is not None
            else None
        )

        payment_id = (
            payment.get(
                "id"
            )
        )

        order_id = (
            payment.get(
                "order_id"
            )
        )

        payment_status = (
            payment.get(
                "status"
            )
        )

        currency = (
            payment.get(
                "currency"
            )
        )

        payment_method = (
            payment.get(
                "method"
            )
        )

        email = (
            payment.get(
                "email"
            )
        )

        contact = (
            payment.get(
                "contact"
            )
        )

        created_at = (
            payment.get(
                "created_at"
            )
        )

        captured = (
            payment.get(
                "captured"
            )
        )

        amount_refunded = (
            payment.get(
                "amount_refunded"
            )
        )

        # ----------------------------------------------------
        # 5. Audit successful verification
        # ----------------------------------------------------

        audit_logger.log_event(
            event_type=(
                "PAYMENT_VERIFICATION"
            ),

            payment_id=
                payment_id,

            action=
                "VERIFY_PAYMENT",

            status=
                "VERIFIED",

            details={
                "order_id":
                    order_id,

                "amount":
                    amount_rupees,

                "currency":
                    currency,

                "payment_status":
                    payment_status,

                "payment_method":
                    payment_method,

                "captured":
                    captured,

                "amount_refunded":
                    (
                        float(
                            amount_refunded
                        ) / 100
                        if amount_refunded is not None
                        else None
                    ),

                "email":
                    email,

                "contact":
                    contact,

                "created_at":
                    created_at,
            },
        )

        # ----------------------------------------------------
        # 6. Return trusted payment data
        # ----------------------------------------------------

        return {
            "verified":
                True,

            "status":
                "verified",

            "payment": {
                "payment_id":
                    payment_id,

                "order_id":
                    order_id,

                "amount":
                    amount_rupees,

                "currency":
                    currency,

                "payment_status":
                    payment_status,

                "payment_method":
                    payment_method,

                "captured":
                    captured,

                "amount_refunded":
                    (
                        float(
                            amount_refunded
                        ) / 100
                        if amount_refunded is not None
                        else None
                    ),

                "email":
                    email,

                "contact":
                    contact,

                "created_at":
                    created_at,
            },
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

        df = (
            load_payment_data(
                source
            )
        )

        if df.empty:

            return {
                "source":
                    source,

                "total_payments":
                    0,

                "failed_payments":
                    0,

                "captured_payments":
                    0,

                "failure_rate":
                    0.0,

                "revenue_at_risk":
                    0.0,
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

        total_payments = len(
            df
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
            "source":
                source,

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

        result = (
            run_merchantops(
                source
            )
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
                result[
                    "decision_records"
                ],
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc

# ============================================================
# RAZORPAY WEBHOOK
# ============================================================

@app.post(
    "/webhooks/razorpay"
)
async def razorpay_webhook(
    request: Request,
) -> Dict[str, Any]:
    """
    Receive, verify, deduplicate, audit, and process
    Razorpay webhook events.

    Razorpay webhook idempotency uses the
    x-razorpay-event-id request header.
    """

    try:

        # ----------------------------------------------------
        # 1. Read exact raw request body
        # ----------------------------------------------------

        payload = (
            await request.body()
        )

        # ----------------------------------------------------
        # 2. Read Razorpay webhook signature
        # ----------------------------------------------------

        signature = (
            request.headers.get(
                "X-Razorpay-Signature"
            )
        )

        if not signature:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Missing "
                    "X-Razorpay-Signature header."
                ),
            )

        # ----------------------------------------------------
        # 3. Read Razorpay event ID
        #
        # This is the official idempotency identifier.
        # ----------------------------------------------------

        event_id = (
            request.headers.get(
                "x-razorpay-event-id"
            )
        )

        if not event_id:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Missing "
                    "x-razorpay-event-id header."
                ),
            )

        # ----------------------------------------------------
        # 4. Verify webhook signature BEFORE parsing body
        # ----------------------------------------------------

        verifier = (
            RazorpayWebhookVerifier()
        )

        valid = verifier.verify(
            payload,
            signature,
        )

        if not valid:

            raise HTTPException(
                status_code=401,
                detail=(
                    "Invalid webhook signature."
                ),
            )

        # ----------------------------------------------------
        # 5. Parse JSON after signature verification
        # ----------------------------------------------------

        try:

            event = json.loads(
                payload.decode(
                    "utf-8"
                )
            )

        except json.JSONDecodeError as exc:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid JSON webhook payload."
                ),
            ) from exc

        # ----------------------------------------------------
        # 6. Extract event information
        # ----------------------------------------------------

        event_name = str(
            event.get(
                "event",
                "unknown",
            )
        )

        payload_data = (
            event.get(
                "payload",
                {}
            )
        )

        payment_entity = (
            payload_data
            .get(
                "payment",
                {}
            )
            .get(
                "entity",
                {}
            )
        )

        payment_id = (
            payment_entity.get(
                "id"
            )
        )

        order_id = (
            payment_entity.get(
                "order_id"
            )
        )

        payment_status = (
            payment_entity.get(
                "status"
            )
        )

        amount = (
            payment_entity.get(
                "amount"
            )
        )

        # ----------------------------------------------------
        # 7. PostgreSQL idempotency check
        # ----------------------------------------------------

        if webhook_event_store.exists(
            event_id
        ):

            return {
                "status":
                    "duplicate",

                "event":
                    event_name,

                "event_id":
                    event_id,

                "payment_id":
                    payment_id,

                "message":
                    (
                        "Webhook already "
                        "processed."
                    ),
            }

        # ----------------------------------------------------
        # 8. Audit webhook reception
        # ----------------------------------------------------

        audit_event = (
            audit_logger.log_event(
                event_type=
                    "RAZORPAY_WEBHOOK",

                payment_id=
                    payment_id,

                action=
                    event_name,

                status=
                    "RECEIVED",

                details={
                    "event_id":
                        event_id,

                    "order_id":
                        order_id,

                    "payment_status":
                        payment_status,

                    "amount":
                        (
                            float(amount) / 100
                            if amount is not None
                            else None
                        ),

                    "event":
                        event,
                },
            )
        )

        # ----------------------------------------------------
        # 9. Event classification
        # ----------------------------------------------------

        if event_name == (
            "payment.failed"
        ):

            processing_status = (
                "PAYMENT_FAILED_RECORDED"
            )

        elif event_name == (
            "payment.captured"
        ):

            processing_status = (
                "PAYMENT_CAPTURED_RECORDED"
            )

        elif event_name == (
            "payment.authorized"
        ):

            processing_status = (
                "PAYMENT_AUTHORIZED_RECORDED"
            )

        else:

            processing_status = (
                "EVENT_RECORDED"
            )

        # ----------------------------------------------------
        # 10. Trigger MerchantOps
        # ----------------------------------------------------

        merchantops_result = None

        if payment_id:

            merchantops_result = (
                webhook_processor.process(
                    event_name=
                        event_name,

                    payment_id=
                        payment_id,
                )
            )

        # ----------------------------------------------------
        # 11. Store idempotency event
        # ----------------------------------------------------

        webhook_event_store.record(
            event_id=
                event_id,

            event_name=
                event_name,

            payment_id=
                payment_id,
        )

        # ----------------------------------------------------
        # 12. Return response
        # ----------------------------------------------------

        return {
            "status":
                "accepted",

            "event":
                event_name,

            "event_id":
                event_id,

            "payment_id":
                payment_id,

            "order_id":
                order_id,

            "payment_status":
                payment_status,

            "processing_status":
                processing_status,

            "merchantops_processed":
                bool(
                    merchantops_result
                    and merchantops_result.get(
                        "processed",
                        False,
                    )
                ),

            "merchantops":
                merchantops_result,

            "audit_recorded":
                bool(
                    audit_event
                ),
        }

    except HTTPException:

        raise

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc