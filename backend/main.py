from __future__ import annotations

import json
import os

from datetime import (
    datetime,
    timezone,
)

from typing import (
    Any,
    Dict,
)

import pandas as pd

from dotenv import load_dotenv

from fastapi import (
    FastAPI,
    HTTPException,
    Query,
    Request,
)

from fastapi.middleware.cors import (
    CORSMiddleware,
)

from pydantic import (
    BaseModel,
)

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
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="MerchantOps AI",

    description=(
        "AI-powered merchant intelligence, revenue recovery, "
        "risk analysis, simulation, decision automation, "
        "payment verification, webhook processing, and "
        "governed payment operations."
    ),

    version="2.5.0",
)


# ============================================================
# CONFIGURATION
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

    allow_origins=
        cors_origins,

    allow_credentials=False,

    allow_methods=[
        "*"
    ],

    allow_headers=[
        "*"
    ],
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
# APPLICATION COMPONENTS
# ============================================================

audit_logger = (
    AuditLogger()
)

webhook_processor = (
    RazorpayWebhookProcessor(
        audit_logger=
            audit_logger
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

        "source":
            source,

        "operations": {

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
        },

        "recovery_candidates":
            0,

        "risk_candidates":
            0,

        "simulated_candidates":
            0,

        "decisions":
            0,

        "action_counts": {

            "RETRY_NOW":
                0,

            "RETRY_LATER":
                0,

            "REVIEW":
                0,

            "DO_NOTHING":
                0,
        },

        "execution_modes": {

            "MERCHANT_APPROVAL":
                0,

            "SCHEDULED_TEST_ACTION":
                0,

            "BLOCKED":
                0,

            "NO_ACTION":
                0,
        },

        "approval_required":
            0,

        "allowed_actions":
            0,

        "blocked_actions":
            0,

        "decision_records":
            [],
    }


# ============================================================
# MERCHANTOPS PIPELINE
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

            return (
                empty_analysis(
                    source
                )
            )

        orchestrator = (
            MerchantOpsOrchestrator(
                payments_df
            )
        )

        result = (
            orchestrator.run()
        )

        result[
            "source"
        ] = source

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

        "version":
            app.version,

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

        "activity_stats":
            "/activity/stats",

        "audit":
            "/audit",

        "webhook_events":
            "/webhooks/events",

        "verified_payments":
            "/payments/verified",
    }


# ============================================================
# HEALTH
# ============================================================

@app.get(
    "/health"
)
def health() -> Dict[str, str]:
    """
    Basic API health check.
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
    Check PostgreSQL connectivity and record counts.
    """

    try:

        database_url = os.getenv(
            "DATABASE_URL"
        )

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

        database = (
            PostgresDatabase(
                database_url
            )
        )

        database.initialize()

        stats = (
            database.get_stats()
        )

        return {

            "api":
                "healthy",

            "database":
                "healthy",

            "audit_logs":
                stats[
                    "audit_logs"
                ],

            "webhook_events":
                stats[
                    "webhook_events"
                ],
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
# ACTIVITY STATISTICS
# ============================================================

@app.get(
    "/activity/stats"
)
def activity_stats() -> Dict[str, Any]:
    """
    Return aggregate MerchantOps activity statistics.

    Production counts come directly from PostgreSQL.
    """

    try:

        database_url = os.getenv(
            "DATABASE_URL"
        )

        # ----------------------------------------------------
        # Production
        # ----------------------------------------------------

        if database_url:

            database = (
                PostgresDatabase(
                    database_url
                )
            )

            database.initialize()

            stats = (
                database.get_activity_stats()
            )

            return {

                "storage":
                    "postgresql",

                "verified_payments":
                    stats[
                        "verified_payments"
                    ],

                "verification_events":
                    stats[
                        "verification_events"
                    ],

                "webhook_events":
                    stats[
                        "webhook_events"
                    ],

                "webhook_processing":
                    stats[
                        "webhook_processing"
                    ],
            }

        # ----------------------------------------------------
        # Local fallback
        # ----------------------------------------------------

        events = (
            audit_logger.read_events()
        )

        verification_events = [
            event

            for event in events

            if event.get(
                "event_type"
            )
            ==
            "PAYMENT_VERIFICATION"
        ]

        verified_payments = [
            event

            for event in verification_events

            if event.get(
                "status"
            )
            ==
            "VERIFIED"
        ]

        webhook_processing = [
            event

            for event in events

            if event.get(
                "event_type"
            )
            ==
            "WEBHOOK_PROCESSING"
        ]

        return {

            "storage":
                "local",

            "verified_payments":
                len(
                    verified_payments
                ),

            "verification_events":
                len(
                    verification_events
                ),

            "webhook_events":
                0,

            "webhook_processing":
                len(
                    webhook_processing
                ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# AUDIT EVENTS
# ============================================================

@app.get(
    "/audit"
)
def get_audit_events(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
        description=(
            "Maximum number of audit events to return."
        ),
    ),
) -> Dict[str, Any]:
    """
    Return audit events.
    """

    try:

        database_url = os.getenv(
            "DATABASE_URL"
        )

        if database_url:

            database = (
                PostgresDatabase(
                    database_url
                )
            )

            database.initialize()

            events = (
                database
                .read_recent_audit_events(
                    limit
                )
            )

            return {

                "count":
                    len(events),

                "events":
                    events,

                "storage":
                    "postgresql",
            }

        events = (
            audit_logger.read_events()
        )

        events = (
            events[
                -limit:
            ][::-1]
        )

        return {

            "count":
                len(events),

            "events":
                events,

            "storage":
                "local",
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# WEBHOOK EVENTS
# ============================================================

@app.get(
    "/webhooks/events"
)
def get_webhook_events() -> Dict[str, Any]:
    """
    Return stored Razorpay webhook events.
    """

    try:

        database_url = os.getenv(
            "DATABASE_URL"
        )

        if database_url:

            database = (
                PostgresDatabase(
                    database_url
                )
            )

            database.initialize()

            events = (
                database
                .read_webhook_events()
            )

            return {

                "count":
                    len(events),

                "events":
                    events,

                "storage":
                    "postgresql",
            }

        return {

            "count":
                0,

            "events":
                [],

            "storage":
                "local",
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# VERIFIED PAYMENTS
# ============================================================

@app.get(
    "/payments/verified"
)
def get_verified_payments() -> Dict[str, Any]:
    """
    Return successfully verified Razorpay payments.
    """

    try:

        database_url = os.getenv(
            "DATABASE_URL"
        )

        if database_url:

            database = (
                PostgresDatabase(
                    database_url
                )
            )

            database.initialize()

            events = (
                database
                .read_audit_events()
            )

            storage = (
                "postgresql"
            )

        else:

            events = (
                audit_logger.read_events()
            )

            storage = (
                "local"
            )

        verified = []

        for event in events:

            if (
                event.get(
                    "event_type"
                )
                !=
                "PAYMENT_VERIFICATION"
            ):

                continue

            if (
                event.get(
                    "status"
                )
                !=
                "VERIFIED"
            ):

                continue

            payment_id = (
                event.get(
                    "payment_id"
                )
            )

            if not payment_id:

                continue

            details = (
                event.get(
                    "details",
                    {}
                )
            )

            verified.append(
                {

                    "timestamp":
                        event.get(
                            "timestamp"
                        ),

                    "payment_id":
                        payment_id,

                    "order_id":
                        details.get(
                            "order_id"
                        ),

                    "amount":
                        details.get(
                            "amount"
                        ),

                    "currency":
                        details.get(
                            "currency"
                        ),

                    "payment_status":
                        details.get(
                            "payment_status"
                        ),

                    "payment_method":
                        details.get(
                            "payment_method"
                        ),

                    "captured":
                        details.get(
                            "captured"
                        ),

                    "amount_refunded":
                        details.get(
                            "amount_refunded"
                        ),

                    "email":
                        details.get(
                            "email"
                        ),

                    "contact":
                        details.get(
                            "contact"
                        ),
                }
            )

        verified.reverse()

        return {

            "count":
                len(
                    verified
                ),

            "payments":
                verified,

            "storage":
                storage,
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


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
    Create Razorpay Test Mode order.
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
    payload:
        PaymentVerificationRequest,
) -> Dict[str, Any]:
    """
    Verify Razorpay Checkout payment signature.

    Successful flow:

        Checkout
            ↓
        Signature verification
            ↓
        Razorpay payment lookup
            ↓
        PostgreSQL audit_logs
            ↓
        /payments/verified
    """

    try:

        client = (
            RazorpayClient()
        )

        # ----------------------------------------------------
        # 1. Verify signature
        # ----------------------------------------------------

        verified = (
            client.verify_payment_signature(

                order_id=
                    payload.razorpay_order_id,

                payment_id=
                    payload.razorpay_payment_id,

                signature=
                    payload.razorpay_signature,
            )
        )

        # ----------------------------------------------------
        # 2. Rejected signature
        # ----------------------------------------------------

        if not verified:

            verification_event = {

                "timestamp":
                    datetime.now(
                        timezone.utc
                    ).isoformat(),

                "event_type":
                    "PAYMENT_VERIFICATION",

                "payment_id":
                    payload.razorpay_payment_id,

                "decision":
                    None,

                "action":
                    "VERIFY_PAYMENT",

                "risk_level":
                    None,

                "approval_required":
                    None,

                "execution_mode":
                    None,

                "status":
                    "REJECTED",

                "details": {

                    "order_id":
                        payload.razorpay_order_id,

                    "reason":
                        (
                            "Invalid Razorpay "
                            "payment signature."
                        ),
                },
            }

            database_url = os.getenv(
                "DATABASE_URL"
            )

            if database_url:

                database = (
                    PostgresDatabase(
                        database_url
                    )
                )

                database.initialize()

                database.insert_audit_event(
                    verification_event
                )

                audit_storage = (
                    "postgresql"
                )

            else:

                audit_logger.log_event(

                    event_type=
                        "PAYMENT_VERIFICATION",

                    payment_id=
                        payload.razorpay_payment_id,

                    action=
                        "VERIFY_PAYMENT",

                    status=
                        "REJECTED",

                    details=
                        verification_event[
                            "details"
                        ],
                )

                audit_storage = (
                    "local"
                )

            return {

                "verified":
                    False,

                "status":
                    "rejected",

                "audit_recorded":
                    True,

                "audit_storage":
                    audit_storage,

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
        # 3. Fetch trusted payment
        # ----------------------------------------------------

        payment = (
            client.fetch_payment(
                payload.razorpay_payment_id
            )
        )

        # ----------------------------------------------------
        # 4. Extract trusted values
        # ----------------------------------------------------

        amount_paise = (
            payment.get(
                "amount"
            )
        )

        amount_rupees = (

            float(
                amount_paise
            ) / 100

            if amount_paise is not None

            else None
        )

        payment_id = (

            payment.get(
                "id"
            )

            or

            payload.razorpay_payment_id
        )

        order_id = (

            payment.get(
                "order_id"
            )

            or

            payload.razorpay_order_id
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

        amount_refunded_rupees = (

            float(
                amount_refunded
            ) / 100

            if amount_refunded is not None

            else None
        )

        # ----------------------------------------------------
        # 5. Build verification event
        # ----------------------------------------------------

        verification_event = {

            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "event_type":
                "PAYMENT_VERIFICATION",

            "payment_id":
                payment_id,

            "decision":
                None,

            "action":
                "VERIFY_PAYMENT",

            "risk_level":
                None,

            "approval_required":
                None,

            "execution_mode":
                None,

            "status":
                "VERIFIED",

            "details": {

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
                    amount_refunded_rupees,

                "email":
                    email,

                "contact":
                    contact,

                "created_at":
                    created_at,
            },
        }

        # ----------------------------------------------------
        # 6. Persist directly
        # ----------------------------------------------------

        database_url = os.getenv(
            "DATABASE_URL"
        )

        if database_url:

            database = (
                PostgresDatabase(
                    database_url
                )
            )

            database.initialize()

            database.insert_audit_event(
                verification_event
            )

            audit_recorded = True

            audit_storage = (
                "postgresql"
            )

        else:

            audit_logger.log_event(

                event_type=
                    "PAYMENT_VERIFICATION",

                payment_id=
                    payment_id,

                action=
                    "VERIFY_PAYMENT",

                status=
                    "VERIFIED",

                details=
                    verification_event[
                        "details"
                    ],
            )

            audit_recorded = True

            audit_storage = (
                "local"
            )

        # ----------------------------------------------------
        # 7. Return
        # ----------------------------------------------------

        return {

            "verified":
                True,

            "status":
                "verified",

            "audit_recorded":
                audit_recorded,

            "audit_storage":
                audit_storage,

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
                    amount_refunded_rupees,

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

@app.get(
    "/payments"
)
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

@app.get(
    "/analyze"
)
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
    Run complete MerchantOps AI analysis.
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

@app.get(
    "/decisions"
)
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
                result["decision_records"],
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

    Idempotency uses:
        x-razorpay-event-id
    """

    try:

        # ----------------------------------------------------
        # 1. Read raw body
        # ----------------------------------------------------

        payload = (
            await request.body()
        )

        # ----------------------------------------------------
        # 2. Signature
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
        # 3. Event ID
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
        # 4. Verify webhook signature
        # ----------------------------------------------------

        verifier = (
            RazorpayWebhookVerifier()
        )

        valid = (
            verifier.verify(
                payload,
                signature,
            )
        )

        if not valid:

            raise HTTPException(
                status_code=401,
                detail=(
                    "Invalid webhook signature."
                ),
            )

        # ----------------------------------------------------
        # 5. Parse webhook
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
        # 6. Extract event data
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
        # 7. Idempotency
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
        # 8. Audit webhook receipt
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
                            float(
                                amount
                            ) / 100

                            if amount is not None

                            else None
                        ),

                    "event":
                        event,
                },
            )
        )

        # ----------------------------------------------------
        # 9. Classify webhook
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
        # 10. MerchantOps
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
        # 11. Record webhook
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
        # 12. Return
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