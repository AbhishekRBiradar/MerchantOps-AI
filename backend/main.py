from __future__ import annotations
from backend.api.catalog import router as catalog_router
from backend.api.buyer import router as buyer_router
from backend.api.cart import router as cart_router
import hashlib
import json
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import pandas as pd
from dotenv import load_dotenv
from fastapi import Body, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.agents.orchestrator import MerchantOpsOrchestrator
from backend.database.audit import AuditLogger
from backend.database.postgres import PostgresDatabase
from backend.database.webhook_events import WebhookEventStore
from backend.tools.payment_provider import PaymentProvider
from backend.tools.webhook_processor import RazorpayWebhookProcessor
from razorpay.client import RazorpayClient
from razorpay.webhook import RazorpayWebhookVerifier



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
        "Razorpay payment verification, webhook processing, "
        "merchant order management, and governance."
    ),
    version="2.8.0",
)

app.include_router(
    catalog_router
)

app.include_router(
    buyer_router
)

app.include_router(
    cart_router
)

# ============================================================
# CONFIGURATION
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "https://merchantops-ai-api.onrender.com",
).rstrip("/")

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    (
        "http://127.0.0.1:5500,"
        "http://localhost:5500,"
        "http://127.0.0.1:8501,"
        "http://localhost:8501"
    ),
)

cors_origins = [
    origin.strip()
    for origin in CORS_ORIGINS.split(",")
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

class PaymentVerificationRequest(BaseModel):
    """Razorpay Checkout payment verification payload."""

    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class CreateOrderRequest(BaseModel):
    """
    Merchant-controlled order request.

    Amounts are expressed in INR except the legacy query
    parameter, which is expressed in paise.

    Example:

    {
        "amount": 1950,
        "currency": "INR",
        "customer_name": "Rahul",
        "customer_email": "rahul@example.com",
        "customer_phone": "9876543210",
        "product_name": "Laptop Backpack",
        "quantity": 2,
        "unit_price": 1000,
        "subtotal": 2000,
        "discount": 100,
        "tax": 50,
        "description": "Laptop Backpack - Black"
    }
    """

    amount: Optional[float] = None

    currency: str = "INR"

    customer_name: Optional[str] = None

    customer_email: Optional[str] = None

    customer_phone: Optional[str] = None

    product_name: Optional[str] = None

    quantity: int = 1

    unit_price: float = 0.0

    subtotal: Optional[float] = None

    discount: float = 0.0

    tax: float = 0.0

    description: Optional[str] = (
        "MerchantOps AI Test Payment"
    )


# ============================================================
# APPLICATION COMPONENTS
# ============================================================

audit_logger = AuditLogger()

webhook_processor = RazorpayWebhookProcessor(
    audit_logger=audit_logger
)

webhook_event_store = WebhookEventStore()


# ============================================================
# GENERAL HELPERS
# ============================================================

def get_database_url() -> Optional[str]:
    """Return DATABASE_URL when configured."""

    return os.getenv("DATABASE_URL")


def order_receipt_id() -> str:
    """Generate a unique Razorpay receipt suffix."""

    return datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%d%H%M%S%f"
    )


def normalize_amount_to_rupees(
    amount_paise: Any,
) -> float:
    """Convert paise to INR."""

    return float(amount_paise) / 100


def normalize_datetime(
    value: Any,
) -> Any:
    """Convert datetime-like values to ISO strings."""

    if value is None:
        return None

    if hasattr(value, "isoformat"):
        return value.isoformat()

    return value


def normalize_order_numbers(
    order: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Normalize numeric and datetime fields in a merchant order
    before returning it through the API.
    """

    result = dict(order)

    if result.get("quantity") is not None:
        result["quantity"] = int(
            result["quantity"]
        )

    numeric_fields = [
        "unit_price",
        "subtotal",
        "discount",
        "tax",
        "amount",
    ]

    for field in numeric_fields:
        if result.get(field) is not None:
            result[field] = float(
                result[field]
            )

    for field in [
        "created_at",
        "updated_at",
    ]:
        result[field] = normalize_datetime(
            result.get(field)
        )

    return result


# ============================================================
# MERCHANT ORDER FINANCIAL VALIDATION
# ============================================================

def validate_merchant_order_amount(
    *,
    quantity: int,
    unit_price: float,
    subtotal: Optional[float],
    discount: float,
    tax: float,
    amount: float,
) -> Dict[str, float]:
    """
    Validate the merchant pricing structure.

    Formula:

        subtotal = quantity × unit_price

        final amount =
            subtotal - discount + tax
    """

    if quantity <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Quantity must be greater than zero."
            ),
        )

    if unit_price < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unit price cannot be negative."
            ),
        )

    if discount < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Discount cannot be negative."
            ),
        )

    if tax < 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Tax cannot be negative."
            ),
        )

    calculated_subtotal = (
        float(quantity)
        * float(unit_price)
    )

    if subtotal is None:
        normalized_subtotal = calculated_subtotal

    else:
        normalized_subtotal = float(
            subtotal
        )

        if abs(
            normalized_subtotal
            - calculated_subtotal
        ) > 0.01:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Subtotal mismatch. "
                    f"Expected "
                    f"₹{calculated_subtotal:.2f}, "
                    f"received "
                    f"₹{normalized_subtotal:.2f}."
                ),
            )

    calculated_amount = (
        normalized_subtotal
        - float(discount)
        + float(tax)
    )

    if calculated_amount <= 0:
        raise HTTPException(
            status_code=400,
            detail=(
                "Final order amount must be greater than zero."
            ),
        )

    if abs(
        calculated_amount
        - float(amount)
    ) > 0.01:

        raise HTTPException(
            status_code=400,
            detail=(
                "Final amount mismatch. "
                f"Expected "
                f"₹{calculated_amount:.2f}, "
                f"received "
                f"₹{float(amount):.2f}."
            ),
        )

    return {
        "quantity": float(quantity),
        "unit_price": round(
            float(unit_price),
            2,
        ),
        "subtotal": round(
            normalized_subtotal,
            2,
        ),
        "discount": round(
            float(discount),
            2,
        ),
        "tax": round(
            float(tax),
            2,
        ),
        "amount": round(
            calculated_amount,
            2,
        ),
    }


def build_merchant_order_details(
    *,
    product_name: Optional[str],
    quantity: int,
    unit_price: float,
    subtotal: float,
    discount: float,
    tax: float,
    amount: float,
    currency: str,
    description: Optional[str],
) -> Dict[str, Any]:
    """Build normalized order details for persistence/audit."""

    return {
        "product_name": product_name,
        "quantity": int(quantity),
        "unit_price": round(
            float(unit_price),
            2,
        ),
        "subtotal": round(
            float(subtotal),
            2,
        ),
        "discount": round(
            float(discount),
            2,
        ),
        "tax": round(
            float(tax),
            2,
        ),
        "amount": round(
            float(amount),
            2,
        ),
        "currency": currency,
        "description": description,
    }


# ============================================================
# PAYMENT DATA
# ============================================================

def load_payment_data(
    source: str,
) -> pd.DataFrame:
    """Load payment data from CSV or Razorpay."""

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
# EMPTY ANALYSIS
# ============================================================

def empty_analysis(
    source: str,
) -> Dict[str, Any]:

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
# MERCHANTOPS PIPELINE
# ============================================================

def run_merchantops(
    source: str,
) -> Dict[str, Any]:

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

        result["source"] = source

        return result

    except Exception as exc:

        raise RuntimeError(
            "MerchantOps pipeline failed: "
            f"{exc}"
        ) from exc


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root() -> Dict[str, str]:

    return {
        "service": "MerchantOps AI",
        "status": "running",
        "version": app.version,
        "docs": "/docs",
        "webhook": "/webhooks/razorpay",
        "payment_verification":
            "/razorpay/verify-payment",
        "create_order":
            "/razorpay/create-order",
        "merchant_orders":
            "/merchant/orders",
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

@app.get("/health")
def health() -> Dict[str, str]:

    return {
        "status": "healthy",
        "service": "MerchantOps AI",
    }


# ============================================================
# RAZORPAY FINGERPRINT
# ============================================================

@app.get(
    "/health/razorpay-fingerprint"
)
def razorpay_fingerprint() -> Dict[str, Any]:

    key_id = os.getenv(
        "RAZORPAY_KEY_ID"
    )

    key_secret = os.getenv(
        "RAZORPAY_KEY_SECRET"
    )

    webhook_secret = os.getenv(
        "RAZORPAY_WEBHOOK_SECRET"
    )

    fingerprint = None

    if key_secret:

        fingerprint = (
            hashlib
            .sha256(
                key_secret.encode(
                    "utf-8"
                )
            )
            .hexdigest()[:12]
        )

    return {
        "key_id_present":
            bool(key_id),

        "key_id":
            key_id,

        "key_secret_present":
            bool(key_secret),

        "key_secret_fingerprint":
            fingerprint,

        "webhook_secret_present":
            bool(webhook_secret),
    }


# ============================================================
# DATABASE HEALTH
# ============================================================

@app.get(
    "/health/database"
)
def database_health() -> Dict[str, Any]:

    try:

        database_url = (
            get_database_url()
        )

        if not database_url:

            return {
                "api": "healthy",
                "database": "not_configured",
                "message": (
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
            "api": "healthy",
            "database": "healthy",
            "audit_logs":
                stats["audit_logs"],
            "webhook_events":
                stats["webhook_events"],
        }

    except Exception as exc:

        return {
            "api": "healthy",
            "database": "unhealthy",
            "error": str(exc),
        }


# ============================================================
# ACTIVITY STATS
# ============================================================

@app.get(
    "/activity/stats"
)
def activity_stats() -> Dict[str, Any]:

    try:

        database_url = (
            get_database_url()
        )

        if database_url:

            database = (
                PostgresDatabase(
                    database_url
                )
            )

            database.initialize()

            stats = (
                database
                .get_activity_stats()
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

        events = (
            audit_logger.read_events()
        )

        verification_events = [
            event
            for event in events
            if event.get(
                "event_type"
            ) == "PAYMENT_VERIFICATION"
        ]

        verified_payments = [
            event
            for event
            in verification_events
            if event.get(
                "status"
            ) == "VERIFIED"
        ]

        webhook_processing = [
            event
            for event in events
            if event.get(
                "event_type"
            ) == "WEBHOOK_PROCESSING"
        ]

        return {
            "storage": "local",

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
# AUDIT
# ============================================================

@app.get("/audit")
def get_audit_events(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
) -> Dict[str, Any]:

    try:

        database_url = (
            get_database_url()
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

    try:

        database_url = (
            get_database_url()
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
            "count": 0,
            "events": [],
            "storage": "local",
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

    try:

        database_url = (
            get_database_url()
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
                    {},
                )
                or {}
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
                len(verified),

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
# CREATE RAZORPAY ORDER
# ============================================================

@app.post(
    "/razorpay/create-order"
)
def create_razorpay_order(
    amount: Optional[int] = Query(
        default=None,
        description=(
            "Legacy amount in paise. "
            "Example: ₹500 = 50000."
        ),
    ),

    body: Optional[
        CreateOrderRequest
    ] = Body(
        default=None
    ),
) -> Dict[str, Any]:

    try:

        # ====================================================
        # LEGACY QUERY MODE
        # ====================================================

        if body is None:

            if amount is None:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Amount is required."
                    ),
                )

            if amount <= 0:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Amount must be greater than zero."
                    ),
                )

            amount_paise = int(
                amount
            )

            amount_rupees = (
                amount_paise / 100
            )

            currency = "INR"

            customer_name = None
            customer_email = None
            customer_phone = None

            product_name = None

            quantity = 1

            unit_price = (
                amount_rupees
            )

            subtotal = (
                amount_rupees
            )

            discount = 0.0
            tax = 0.0

            description = (
                "MerchantOps AI Test Payment"
            )

        # ====================================================
        # MERCHANT JSON MODE
        # ====================================================

        else:

            if body.amount is None:

                raise HTTPException(
                    status_code=400,
                    detail="amount is required.",
                )

            if body.amount <= 0:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Amount must be greater than zero."
                    ),
                )

            currency = (
                body.currency
                or
                "INR"
            ).upper()

            if currency != "INR":

                raise HTTPException(
                    status_code=400,
                    detail=(
                        "Currently only INR "
                        "orders are supported."
                    ),
                )

            customer_name = (
                body.customer_name
            )

            customer_email = (
                body.customer_email
            )

            customer_phone = (
                body.customer_phone
            )

            product_name = (
                body.product_name
            )

            quantity = int(
                body.quantity
            )

            unit_price = float(
                body.unit_price
            )

            discount = float(
                body.discount
            )

            tax = float(
                body.tax
            )

            amount_rupees = float(
                body.amount
            )

            breakdown = (
                validate_merchant_order_amount(

                    quantity=
                        quantity,

                    unit_price=
                        unit_price,

                    subtotal=
                        body.subtotal,

                    discount=
                        discount,

                    tax=
                        tax,

                    amount=
                        amount_rupees,
                )
            )

            quantity = int(
                breakdown[
                    "quantity"
                ]
            )

            unit_price = (
                breakdown[
                    "unit_price"
                ]
            )

            subtotal = (
                breakdown[
                    "subtotal"
                ]
            )

            discount = (
                breakdown[
                    "discount"
                ]
            )

            tax = (
                breakdown[
                    "tax"
                ]
            )

            amount_rupees = (
                breakdown[
                    "amount"
                ]
            )

            description = (
                body.description
                or
                product_name
                or
                "MerchantOps AI Test Payment"
            )


        # ====================================================
        # RAZORPAY AMOUNT
        # ====================================================

        amount_paise = int(
            round(
                amount_rupees * 100
            )
        )


        if amount_paise <= 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Amount must result in "
                    "at least 1 paise."
                ),
            )


        # ====================================================
        # RAZORPAY ORDER
        # ====================================================

        client = (
            RazorpayClient()
        )


        order = (
            client.create_order(

                amount=
                    amount_paise,

                currency=
                    currency,

                receipt=(
                    "merchantops_"
                    +
                    order_receipt_id()
                ),
            )
        )


        razorpay_order_id = (
            order["id"]
        )


        # ====================================================
        # ORDER DETAILS
        # ====================================================

        merchant_order_details = (
            build_merchant_order_details(

                product_name=
                    product_name,

                quantity=
                    quantity,

                unit_price=
                    unit_price,

                subtotal=
                    subtotal,

                discount=
                    discount,

                tax=
                    tax,

                amount=
                    amount_rupees,

                currency=
                    currency,

                description=
                    description,
            )
        )


        # ====================================================
        # POSTGRESQL
        # ====================================================

        database_url = (
            get_database_url()
        )

        merchant_order = None


        if database_url:

            database = (
                PostgresDatabase(
                    database_url
                )
            )

            database.initialize()

            merchant_order = (
                database
                .create_merchant_order(

                    order_id=
                        razorpay_order_id,

                    amount=
                        amount_rupees,

                    currency=
                        currency,

                    customer_name=
                        customer_name,

                    customer_email=
                        customer_email,

                    customer_phone=
                        customer_phone,

                    product_name=
                        product_name,

                    quantity=
                        quantity,

                    unit_price=
                        unit_price,

                    subtotal=
                        subtotal,

                    discount=
                        discount,

                    tax=
                        tax,

                    description=
                        description,

                    status=
                        "CREATED",
                )
            )


        # ====================================================
        # LOCAL AUDIT
        # ====================================================

        audit_logger.log_event(

            event_type=
                "RAZORPAY_ORDER_CREATED",

            action=
                "CREATE_ORDER",

            status=
                "CREATED",

            details={

                "order_id":
                    razorpay_order_id,

                "customer_name":
                    customer_name,

                "customer_email":
                    customer_email,

                "customer_phone":
                    customer_phone,

                **merchant_order_details,

                "storage":
                    (
                        "postgresql"
                        if database_url
                        else "local"
                    ),
            },
        )


        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "order_id":
                razorpay_order_id,

            "amount":
                order["amount"],

            "currency":
                order["currency"],

            "status":
                order["status"],

            "customer": {

                "name":
                    customer_name,

                "email":
                    customer_email,

                "phone":
                    customer_phone,
            },

            "order": {

                "product_name":
                    product_name,

                "quantity":
                    quantity,

                "unit_price":
                    unit_price,

                "subtotal":
                    subtotal,

                "discount":
                    discount,

                "tax":
                    tax,

                "final_amount":
                    amount_rupees,

                "currency":
                    currency,

                "description":
                    description,
            },

            "description":
                description,

            "storage":
                (
                    "postgresql"
                    if database_url
                    else "local"
                ),

            "merchant_order":
                merchant_order,
        }


    except HTTPException:

        raise


    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# VERIFY RAZORPAY PAYMENT
# ============================================================

@app.post(
    "/razorpay/verify-payment"
)
def verify_razorpay_payment(
    payload:
        PaymentVerificationRequest,
) -> Dict[str, Any]:

    try:

        client = (
            RazorpayClient()
        )


        # ====================================================
        # SIGNATURE VERIFICATION
        # ====================================================

        verified = (
            client
            .verify_payment_signature(

                order_id=
                    payload.razorpay_order_id,

                payment_id=
                    payload.razorpay_payment_id,

                signature=
                    payload.razorpay_signature,
            )
        )


        # ====================================================
        # INVALID SIGNATURE
        # ====================================================

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


            database_url = (
                get_database_url()
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


        # ====================================================
        # FETCH TRUSTED RAZORPAY PAYMENT
        # ====================================================

        payment = (
            client.fetch_payment(
                payload.razorpay_payment_id
            )
        )


        amount_paise = (
            payment.get(
                "amount"
            )
        )


        amount_rupees = (

            normalize_amount_to_rupees(
                amount_paise
            )

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

            normalize_amount_to_rupees(
                amount_refunded
            )

            if amount_refunded is not None
            else None
        )


        # ====================================================
        # VERIFICATION EVENT
        # ====================================================

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


        # ====================================================
        # PERSIST VERIFICATION
        # ====================================================

        database_url = (
            get_database_url()
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


            database.update_merchant_order(

                order_id=
                    order_id,

                status=
                    "VERIFIED",

                payment_id=
                    payment_id,
            )


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


            audit_storage = (
                "local"
            )


        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "verified":
                True,

            "status":
                "verified",

            "audit_recorded":
                True,

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
# LOCAL ORDER RECONSTRUCTION
# ============================================================

def reconstruct_local_orders(
    events: List[Dict[str, Any]],
) -> Dict[str, Dict[str, Any]]:
    """
    Reconstruct merchant orders from the local audit trail.

    This is important for local development where PostgreSQL
    is not configured.

    New order records contain the full commercial breakdown:

        product_name
        quantity
        unit_price
        subtotal
        discount
        tax
        amount
    """

    orders_by_id: Dict[
        str,
        Dict[str, Any],
    ] = {}


    # ========================================================
    # ORDER CREATION EVENTS
    # ========================================================

    for event in events:

        if (
            event.get(
                "event_type"
            )
            !=
            "RAZORPAY_ORDER_CREATED"
        ):
            continue


        details = (
            event.get(
                "details",
                {},
            )
            or {}
        )


        order_id = (
            details.get(
                "order_id"
            )
        )


        if not order_id:
            continue


        orders_by_id[
            order_id
        ] = {

            "order_id":
                order_id,

            "customer_name":
                details.get(
                    "customer_name"
                ),

            "customer_email":
                details.get(
                    "customer_email"
                ),

            "customer_phone":
                details.get(
                    "customer_phone"
                ),

            # -----------------------------------------------
            # COMPLETE COMMERCIAL BREAKDOWN
            # -----------------------------------------------

            "product_name":
                details.get(
                    "product_name"
                ),

            "quantity":
                details.get(
                    "quantity",
                    1,
                ),

            "unit_price":
                details.get(
                    "unit_price"
                ),

            "subtotal":
                details.get(
                    "subtotal"
                ),

            "discount":
                details.get(
                    "discount",
                    0.0,
                ),

            "tax":
                details.get(
                    "tax",
                    0.0,
                ),

            "amount":
                details.get(
                    "amount"
                ),

            "currency":
                details.get(
                    "currency",
                    "INR",
                ),

            "description":
                details.get(
                    "description"
                ),

            "status":
                "CREATED",

            "payment_id":
                None,

            "created_at":
                event.get(
                    "timestamp"
                ),

            "updated_at":
                event.get(
                    "timestamp"
                ),
        }


    # ========================================================
    # PAYMENT VERIFICATION EVENTS
    # ========================================================

    for event in events:

        if (
            event.get(
                "event_type"
            )
            !=
            "PAYMENT_VERIFICATION"
        ):
            continue


        details = (
            event.get(
                "details",
                {},
            )
            or {}
        )


        order_id = (
            details.get(
                "order_id"
            )
        )


        if not order_id:
            continue


        payment_id = (
            event.get(
                "payment_id"
            )
        )


        verification_status = (
            event.get(
                "status"
            )
        )


        # ----------------------------------------------------
        # Create fallback order if only verification exists.
        # ----------------------------------------------------

        if order_id not in orders_by_id:

            orders_by_id[
                order_id
            ] = {

                "order_id":
                    order_id,

                "customer_name":
                    None,

                "customer_email":
                    details.get(
                        "email"
                    ),

                "customer_phone":
                    details.get(
                        "contact"
                    ),

                "product_name":
                    None,

                "quantity":
                    1,

                "unit_price":
                    None,

                "subtotal":
                    None,

                "discount":
                    0.0,

                "tax":
                    0.0,

                "amount":
                    details.get(
                        "amount"
                    ),

                "currency":
                    details.get(
                        "currency",
                        "INR",
                    ),

                "description":
                    None,

                "status":
                    (
                        "VERIFIED"
                        if
                        verification_status
                        ==
                        "VERIFIED"
                        else
                        "UNKNOWN"
                    ),

                "payment_id":
                    payment_id,

                "created_at":
                    event.get(
                        "timestamp"
                    ),

                "updated_at":
                    event.get(
                        "timestamp"
                    ),
            }

            continue


        # ----------------------------------------------------
        # Merge verification information into existing order.
        # ----------------------------------------------------

        order = (
            orders_by_id[
                order_id
            ]
        )


        if payment_id:

            order[
                "payment_id"
            ] = payment_id


        if (
            verification_status
            ==
            "VERIFIED"
        ):

            order[
                "status"
            ] = "VERIFIED"


        order[
            "updated_at"
        ] = event.get(
            "timestamp"
        )


        # ----------------------------------------------------
        # Fill customer/payment fields when missing.
        # ----------------------------------------------------

        if not order.get(
            "customer_email"
        ):

            order[
                "customer_email"
            ] = details.get(
                "email"
            )


        if not order.get(
            "customer_phone"
        ):

            order[
                "customer_phone"
            ] = details.get(
                "contact"
            )


        if order.get(
            "amount"
        ) is None:

            order[
                "amount"
            ] = details.get(
                "amount"
            )


        if not order.get(
            "currency"
        ):

            order[
                "currency"
            ] = details.get(
                "currency",
                "INR",
            )


    # ========================================================
    # NORMALIZE ALL LOCAL ORDERS
    # ========================================================

    for order_id, order in (
        list(
            orders_by_id.items()
        )
    ):

        orders_by_id[
            order_id
        ] = normalize_order_numbers(
            order
        )


    return orders_by_id


# ============================================================
# MERCHANT ORDERS
# ============================================================

@app.get(
    "/merchant/orders"
)
def get_merchant_orders(
    limit: int = Query(
        default=100,
        ge=1,
        le=1000,
    ),
) -> Dict[str, Any]:

    try:

        database_url = (
            get_database_url()
        )


        # ====================================================
        # PRODUCTION
        # ====================================================

        if database_url:

            database = (
                PostgresDatabase(
                    database_url
                )
            )

            database.initialize()

            orders = (
                database
                .list_merchant_orders(
                    limit
                )
            )

            return {

                "count":
                    len(orders),

                "orders":
                    orders,

                "storage":
                    "postgresql",
            }


        # ====================================================
        # LOCAL
        # ====================================================

        events = (
            audit_logger.read_events()
        )


        orders_by_id = (
            reconstruct_local_orders(
                events
            )
        )


        orders = list(
            orders_by_id.values()
        )


        # ----------------------------------------------------
        # Newest first
        # ----------------------------------------------------

        orders.sort(
            key=lambda order:
                order.get(
                    "created_at"
                )
                or
                "",
            reverse=True,
        )


        orders = orders[
            :limit
        ]


        return {

            "count":
                len(orders),

            "orders":
                orders,

            "storage":
                "local",
        }


    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# SINGLE MERCHANT ORDER
# ============================================================

@app.get(
    "/merchant/orders/{order_id}"
)
def get_single_merchant_order(
    order_id: str,
) -> Dict[str, Any]:

    try:

        database_url = (
            get_database_url()
        )


        # ====================================================
        # POSTGRESQL
        # ====================================================

        if database_url:

            database = (
                PostgresDatabase(
                    database_url
                )
            )

            database.initialize()

            order = (
                database
                .get_merchant_order(
                    order_id
                )
            )


            if order is None:

                raise HTTPException(
                    status_code=404,
                    detail=(
                        "Merchant order not found."
                    ),
                )


            return {

                "order":
                    order,

                "storage":
                    "postgresql",
            }


        # ====================================================
        # LOCAL
        # ====================================================

        events = (
            audit_logger.read_events()
        )


        orders_by_id = (
            reconstruct_local_orders(
                events
            )
        )


        order = (
            orders_by_id.get(
                order_id
            )
        )


        if order is None:

            raise HTTPException(
                status_code=404,
                detail=(
                    "Merchant order not found."
                ),
            )


        return {

            "order":
                order,

            "storage":
                "local",
        }


    except HTTPException:

        raise


    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


# ============================================================
# PAYMENTS ANALYTICS
# ============================================================

@app.get(
    "/payments"
)
def payments(
    source: str = Query(
        default="csv",
    ),
) -> Dict[str, Any]:

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
            df[
                "status"
            ]
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
            /
            total_payments
            *
            100

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

@app.get(
    "/decisions"
)
def decisions(
    source: str = Query(
        default="csv",
    ),
) -> Dict[str, Any]:

    try:

        result = (
            run_merchantops(
                source
            )
        )


        return {

            "source":
                result[
                    "source"
                ],

            "count":
                result[
                    "decisions"
                ],

            "action_counts":
                result[
                    "action_counts"
                ],

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


# ============================================================
# RAZORPAY WEBHOOK
# ============================================================

@app.post(
    "/webhooks/razorpay"
)
async def razorpay_webhook(
    request: Request,
) -> Dict[str, Any]:

    try:

        # ====================================================
        # RAW BODY
        # ====================================================

        payload = (
            await request.body()
        )


        # ====================================================
        # SIGNATURE
        # ====================================================

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


        # ====================================================
        # EVENT ID
        # ====================================================

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


        # ====================================================
        # VERIFY WEBHOOK SIGNATURE
        # ====================================================

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


        # ====================================================
        # PARSE JSON
        # ====================================================

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


        # ====================================================
        # EXTRACT EVENT DATA
        # ====================================================

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
            or {}
        )


        payment_wrapper = (
            payload_data.get(
                "payment",
                {}
            )
            or {}
        )


        payment_entity = (
            payment_wrapper.get(
                "entity",
                {}
            )
            or {}
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


        # ====================================================
        # IDEMPOTENCY
        # ====================================================

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

                "order_id":
                    order_id,

                "message":
                    (
                        "Webhook already "
                        "processed."
                    ),
            }


        # ====================================================
        # AUDIT WEBHOOK
        # ====================================================

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

                    "event":
                        event,

                    "event_id":
                        event_id,

                    "order_id":
                        order_id,

                    "payment_status":
                        payment_status,

                    "amount":
                        (
                            normalize_amount_to_rupees(
                                amount
                            )
                            if amount is not None
                            else None
                        ),
                },
            )
        )


        # ====================================================
        # CLASSIFY WEBHOOK
        # ====================================================

        if event_name == (
            "payment.failed"
        ):

            processing_status = (
                "PAYMENT_FAILED_RECORDED"
            )

            merchant_order_status = (
                "FAILED"
            )

        elif event_name == (
            "payment.captured"
        ):

            processing_status = (
                "PAYMENT_CAPTURED_RECORDED"
            )

            merchant_order_status = (
                "CAPTURED"
            )

        elif event_name == (
            "payment.authorized"
        ):

            processing_status = (
                "PAYMENT_AUTHORIZED_RECORDED"
            )

            merchant_order_status = (
                "AUTHORIZED"
            )

        else:

            processing_status = (
                "EVENT_RECORDED"
            )

            merchant_order_status = (
                None
            )


        # ====================================================
        # MERCHANTOPS WEBHOOK PROCESSOR
        # ====================================================

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


        # ====================================================
        # RECORD EVENT ID
        # ====================================================

        webhook_event_store.record(

            event_id=
                event_id,

            event_name=
                event_name,

            payment_id=
                payment_id,
        )


        # ====================================================
        # PRODUCTION DATABASE UPDATE
        # ====================================================

        database_url = (
            get_database_url()
        )


        merchant_order = None


        if (
            database_url
            and
            order_id
            and
            merchant_order_status
        ):

            database = (
                PostgresDatabase(
                    database_url
                )
            )

            database.initialize()


            merchant_order = (
                database
                .update_merchant_order(

                    order_id=
                        order_id,

                    status=
                        merchant_order_status,

                    payment_id=
                        payment_id,
                )
            )


        # ====================================================
        # RESPONSE
        # ====================================================

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

            "merchant_order_status":
                merchant_order_status,

            "merchantops_processed":
                bool(
                    merchantops_result
                    and
                    merchantops_result.get(
                        "processed",
                        False,
                    )
                ),

            "merchantops":
                merchantops_result,

            "merchant_order":
                merchant_order,

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


# ============================================================
# STARTUP
# ============================================================

@app.on_event(
    "startup"
)
def startup() -> None:

    database_url = (
        get_database_url()
    )

    if not database_url:

        return


    database = (
        PostgresDatabase(
            database_url
        )
    )


    database.initialize()