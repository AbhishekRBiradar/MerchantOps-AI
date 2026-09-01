from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# CONFIGURATION
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

CHECKOUT_URL = os.getenv(
    "CHECKOUT_URL",
    "http://127.0.0.1:5500/razorpay/checkout.html",
)

st.set_page_config(
    page_title="MerchantOps AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# STYLING
# ============================================================

st.markdown(
    """
    <style>
    .main-title {
        font-size: 42px;
        font-weight: 800;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 17px;
        opacity: 0.72;
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 750;
        margin-top: 12px;
        margin-bottom: 12px;
    }

    .small-muted {
        font-size: 12px;
        opacity: 0.65;
    }

    .locked-box {
        padding: 12px 14px;
        border-radius: 10px;
        border: 1px solid rgba(90, 140, 255, 0.30);
        background: rgba(90, 140, 255, 0.08);
        font-size: 13px;
        line-height: 1.45;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ============================================================
# API HELPERS
# ============================================================

@st.cache_data(ttl=10)
def fetch_api(endpoint: str) -> Dict[str, Any]:
    response = requests.get(
        f"{API_URL}{endpoint}",
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def post_api(
    endpoint: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    response = requests.post(
        f"{API_URL}{endpoint}",
        json=payload,
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def safe_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or value == "":
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def format_inr(value: Any) -> str:
    return f"₹{safe_float(value):,.2f}"


def normalize_status(value: Any) -> str:
    return str(value or "UNKNOWN").upper()


# ============================================================
# SESSION STATE
# ============================================================

if "last_created_order" not in st.session_state:
    st.session_state["last_created_order"] = None

if "loaded_order_id" not in st.session_state:
    st.session_state["loaded_order_id"] = ""

if "payment_view" not in st.session_state:
    st.session_state["payment_view"] = "Merchant Orders"


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💳 MerchantOps AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Autonomous merchant intelligence, revenue recovery, "
    "risk analysis and governed AI decision automation."
    "</div>",
    unsafe_allow_html=True,
)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header("⚙️ Controls")

    payment_source_label = st.radio(
        "Payment Data Source",
        [
            "Demo Dataset",
            "Razorpay Test Mode",
        ],
        index=0,
    )

    payment_source = (
        "razorpay"
        if payment_source_label == "Razorpay Test Mode"
        else "csv"
    )

    if st.button(
        "🔄 Refresh All Data",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    st.caption("Backend")

    st.code(
        API_URL,
        language="text",
    )

    st.caption(
        f"Active payment source: {payment_source_label}"
    )

    st.caption(
        "Mode: Test / Development"
    )

    st.divider()

    st.caption("Customer Checkout")

    st.code(
        CHECKOUT_URL,
        language="text",
    )


# ============================================================
# LOAD DATA
# ============================================================

try:
    payments_data = fetch_api(
        f"/payments?source={payment_source}"
    )

    analysis_data = fetch_api(
        f"/analyze?source={payment_source}"
    )

    decisions_data = fetch_api(
        f"/decisions?source={payment_source}"
    )

    activity_data = fetch_api(
        "/activity/stats"
    )

    audit_data = fetch_api(
        "/audit?limit=1000"
    )

    webhook_data = fetch_api(
        "/webhooks/events"
    )

    verified_data = fetch_api(
        "/payments/verified"
    )

    merchant_orders_data = fetch_api(
        "/merchant/orders"
    )

except Exception as exc:
    st.error(
        "❌ Unable to connect to MerchantOps API."
    )
    st.code(str(exc))
    st.info(
        "Start FastAPI or check API_URL."
    )
    st.stop()


audit_events = audit_data.get(
    "events",
    [],
) or []

webhook_events = webhook_data.get(
    "events",
    [],
) or []

verified_payments = verified_data.get(
    "payments",
    [],
) or []

merchant_orders = merchant_orders_data.get(
    "orders",
    [],
) or []

decision_records = decisions_data.get(
    "decisions",
    [],
) or []


# ============================================================
# CONNECTION STATUS
# ============================================================

c1, c2 = st.columns(
    [6, 1]
)

with c1:
    st.success(
        "🟢 MerchantOps API Connected"
    )

with c2:
    st.caption("Live API")


st.caption(
    f"Active payment source: **{payment_source_label}**"
)

# ============================================================
# TABS
# ============================================================

tabs = st.tabs(
    [
        "📊 Overview",
        "💰 Create Order",
        "💳 Payments",
        "🤖 AI Recovery",
        "🛡️ Approvals",
        "🔔 Webhooks",
        "📋 Audit",
    ]
)


# ============================================================
# TAB 1 — OVERVIEW
# ============================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">'
        "📊 Merchant Command Center"
        "</div>",
        unsafe_allow_html=True,
    )

    st.caption(
        "A live merchant view of payment health, revenue at risk, "
        "AI recovery opportunities and governance status."
    )

    # ========================================================
    # CORE METRICS
    # ========================================================

    operations = (
        analysis_data.get(
            "operations",
            {},
        )
        or {}
    )

    total_payments = safe_int(
        payments_data.get(
            "total_payments",
            operations.get(
                "total_payments",
                0,
            ),
        )
    )

    failed_payments = safe_int(
        payments_data.get(
            "failed_payments",
            operations.get(
                "failed_payments",
                0,
            ),
        )
    )

    captured_payments = safe_int(
        payments_data.get(
            "captured_payments",
            operations.get(
                "captured_payments",
                0,
            ),
        )
    )

    failure_rate = safe_float(
        payments_data.get(
            "failure_rate",
            operations.get(
                "failure_rate",
                0.0,
            ),
        )
    )

    revenue_at_risk = safe_float(
        payments_data.get(
            "revenue_at_risk",
            operations.get(
                "revenue_at_risk",
                0.0,
            ),
        )
    )

    success_rate = (
        captured_payments
        /
        total_payments
        *
        100
        if total_payments
        else 0.0
    )

    recovery_candidates = safe_int(
        analysis_data.get(
            "recovery_candidates",
            0,
        )
    )

    decisions_count = safe_int(
        analysis_data.get(
            "decisions",
            decisions_data.get(
                "count",
                len(
                    decision_records
                ),
            ),
        )
    )

    expected_recovery = sum(
        safe_float(
            decision.get(
                "expected_recovery",
                0,
            )
        )
        for decision in decision_records
    )

    approval_required = safe_int(
        decisions_data.get(
            "approval_required",
            0,
        )
    )

    allowed_actions = safe_int(
        decisions_data.get(
            "allowed_actions",
            0,
        )
    )

    blocked_actions = safe_int(
        decisions_data.get(
            "blocked_actions",
            0,
        )
    )

    scheduled_test_actions = safe_int(
        (
            decisions_data.get(
                "execution_modes",
                {},
            )
            or {}
        ).get(
            "SCHEDULED_TEST_ACTION",
            0,
        )
    )

    webhook_processing = safe_int(
        activity_data.get(
            "webhook_processing",
            0,
        )
    )

    verified_count = safe_int(
        activity_data.get(
            "verified_payments",
            0,
        )
    )

    webhook_count = safe_int(
        activity_data.get(
            "webhook_events",
            0,
        )
    )


    # ========================================================
    # KPI CARDS
    # ========================================================

    k1, k2, k3, k4, k5 = st.columns(5)

    with k1:

        st.metric(
            "Total Payments",
            f"{total_payments:,}",
        )

    with k2:

        st.metric(
            "Failed Payments",
            f"{failed_payments:,}",
        )

    with k3:

        st.metric(
            "Success Rate",
            f"{success_rate:.1f}%",
        )

    with k4:

        st.metric(
            "Revenue at Risk",
            format_inr(
                revenue_at_risk
            ),
        )

    with k5:

        st.metric(
            "Expected Recovery",
            format_inr(
                expected_recovery
            ),
        )


    st.divider()


    # ========================================================
    # WHAT NEEDS ATTENTION
    # ========================================================

    st.markdown(
        "### 🚨 What Needs Attention?"
    )

    attention_left, attention_right = st.columns(
        2
    )


    with attention_left:

        if failed_payments > 0:

            st.error(
                f"🔴 {failed_payments:,} failed payment(s) "
                f"represent {format_inr(revenue_at_risk)} "
                "of revenue at risk."
            )

        else:

            st.success(
                "🟢 No failed payments detected in the active source."
            )


    with attention_right:

        if approval_required > 0:

            st.warning(
                f"🛡️ {approval_required:,} AI decision(s) "
                "are waiting for merchant approval."
            )

        elif blocked_actions > 0:

            st.error(
                f"🚫 {blocked_actions:,} unsafe action(s) "
                "were blocked by governance."
            )

        else:

            st.success(
                "✅ No merchant action is currently required."
            )


    st.divider()


    # ========================================================
    # QUICK ACTION CENTER
    # ========================================================

    st.markdown(
        "### ⚡ Merchant Action Center"
    )

    q1, q2, q3, q4 = st.columns(4)


    with q1:

        st.metric(
            "Failed Payments",
            f"{failed_payments:,}",
        )

        st.caption(
            format_inr(
                revenue_at_risk
            )
            +
            " revenue at risk"
        )


        if failed_payments > 0:

            if st.button(
                "🔎 Review Failed Payments",
                use_container_width=True,
                key="overview_failed_payments",
            ):

                st.session_state[
                    "payment_view"
                ] = "Merchant Orders"

                st.info(
                    "Open the Payments tab to filter and inspect affected orders."
                )


    with q2:

        st.metric(
            "Pending Approvals",
            f"{approval_required:,}",
        )

        st.caption(
            "Merchant review required"
        )


        if approval_required > 0:

            if st.button(
                "🛡️ Open Approval Queue",
                use_container_width=True,
                key="overview_approvals",
            ):

                st.info(
                    "Open the Approvals tab to review AI decisions."
                )

        else:

            st.button(
                "🛡️ No Approvals",
                use_container_width=True,
                disabled=True,
                key="overview_no_approvals",
            )


    with q3:

        st.metric(
            "Blocked Actions",
            f"{blocked_actions:,}",
        )

        st.caption(
            "Governance prevented unsafe actions"
        )


        if blocked_actions > 0:

            if st.button(
                "🚫 View Governance",
                use_container_width=True,
                key="overview_blocked",
            ):

                st.info(
                    "Open AI Recovery to inspect the governance decision and policy reason."
                )

        else:

            st.button(
                "✅ No Blocked Actions",
                use_container_width=True,
                disabled=True,
                key="overview_no_blocked",
            )


    with q4:

        st.metric(
            "Verified Payments",
            f"{verified_count:,}",
        )

        st.caption(
            f"{webhook_count:,} webhook event(s)"
        )


        if st.button(
            "💳 View Payments",
            use_container_width=True,
            key="overview_verified",
        ):

            st.info(
                "Open the Payments tab to inspect verified payment details."
            )


    st.caption(
        "These controls navigate the merchant through investigation areas. "
        "They do not execute live recovery actions."
    )


    st.divider()


    # ========================================================
    # AI EXECUTIVE VIEW
    # ========================================================

    st.markdown(
        "### 🤖 AI Executive View"
    )

    ai1, ai2, ai3, ai4 = st.columns(4)

    with ai1:

        st.metric(
            "Recovery Candidates",
            recovery_candidates,
        )

    with ai2:

        st.metric(
            "AI Decisions",
            decisions_count,
        )

    with ai3:

        st.metric(
            "Merchant Approval",
            approval_required,
        )

    with ai4:

        st.metric(
            "Blocked Actions",
            blocked_actions,
        )

    st.info(
        "MerchantOps AI evaluates failed payments using "
        "failure signals, risk scoring, recovery simulation "
        "and governed decision rules. Expected recovery is "
        "an estimate, not guaranteed revenue."
    )


    st.divider()


    # ========================================================
    # RECOMMENDED RECOVERY ACTIONS
    # ========================================================

    st.markdown(
        "### 🎯 Recommended Recovery Actions"
    )

    action_counts = (
        decisions_data.get(
            "action_counts",
            {},
        )
        or {}
    )

    action_df = pd.DataFrame(
        {
            "Action": [
                "RETRY_NOW",
                "RETRY_LATER",
                "REVIEW",
                "DO_NOTHING",
            ],

            "Count": [
                safe_int(
                    action_counts.get(
                        "RETRY_NOW",
                        0,
                    )
                ),

                safe_int(
                    action_counts.get(
                        "RETRY_LATER",
                        0,
                    )
                ),

                safe_int(
                    action_counts.get(
                        "REVIEW",
                        0,
                    )
                ),

                safe_int(
                    action_counts.get(
                        "DO_NOTHING",
                        0,
                    )
                ),
            ],
        }
    )


    chart_col, cards_col = st.columns(
        [2.2, 1]
    )


    with chart_col:

        if int(
            action_df[
                "Count"
            ].sum()
        ) > 0:

            st.bar_chart(
                action_df.set_index(
                    "Action"
                )
            )

        else:

            st.info(
                "No recovery actions have been generated yet."
            )


    with cards_col:

        for _, row in action_df.iterrows():

            st.metric(
                str(
                    row["Action"]
                ),
                safe_int(
                    row["Count"]
                ),
            )


    st.divider()


    # ========================================================
    # GOVERNANCE SNAPSHOT
    # ========================================================

    st.markdown(
        "### 🛡️ Governance & Safety Snapshot"
    )

    gov1, gov2, gov3, gov4, gov5 = st.columns(
        5
    )


    with gov1:

        st.metric(
            "Allowed",
            allowed_actions,
        )


    with gov2:

        st.metric(
            "Blocked",
            blocked_actions,
        )


    with gov3:

        st.metric(
            "Approval Required",
            approval_required,
        )


    with gov4:

        st.metric(
            "Scheduled Test",
            scheduled_test_actions,
        )


    with gov5:

        st.metric(
            "Webhook Processing",
            webhook_processing,
        )


    if blocked_actions > 0:

        st.error(
            "🚫 Governance is actively preventing unsafe "
            "automatic actions. Review blocked decisions in "
            "AI Recovery before any merchant intervention."
        )

    elif approval_required > 0:

        st.warning(
            "🛡️ Some AI recommendations require merchant approval "
            "before any action can proceed."
        )

    else:

        st.success(
            "✅ No blocked or approval-pending AI actions."
        )


    st.divider()


    # ========================================================
    # RAZORPAY LIVE ACTIVITY
    # ========================================================

    st.markdown(
        "### 💳 Razorpay Live Activity"
    )

    live1, live2, live3, live4 = st.columns(
        4
    )


    with live1:

        st.metric(
            "Verified Payments",
            verified_count,
        )


    with live2:

        st.metric(
            "Verification Events",
            safe_int(
                activity_data.get(
                    "verification_events",
                    0,
                )
            ),
        )


    with live3:

        st.metric(
            "Webhook Events",
            webhook_count,
        )


    with live4:

        st.metric(
            "Webhook Processing",
            webhook_processing,
        )


    st.divider()


    # ========================================================
    # RECENT VERIFIED PAYMENTS
    # ========================================================

    st.markdown(
        "### ✅ Recently Verified Payments"
    )

    if verified_payments:

        recent_verified_df = pd.DataFrame(
            verified_payments
        )

        st.dataframe(
            recent_verified_df.head(10),
            use_container_width=True,
            height=320,
            hide_index=True,
        )

    else:

        st.info(
            "No verified Razorpay payments found."
        )


    st.divider()


    # ========================================================
    # MERCHANT ORDER SNAPSHOT
    # ========================================================

    st.markdown(
        "### 🧾 Merchant Order Snapshot"
    )

    total_orders = len(
        merchant_orders
    )

    verified_orders = sum(
        1
        for order
        in merchant_orders
        if normalize_status(
            order.get(
                "status"
            )
        )
        in {
            "VERIFIED",
            "CAPTURED",
        }
    )

    pending_orders = sum(
        1
        for order
        in merchant_orders
        if normalize_status(
            order.get(
                "status"
            )
        )
        == "CREATED"
    )

    order_value = sum(
        safe_float(
            order.get(
                "amount"
            )
        )
        for order
        in merchant_orders
    )


    o1, o2, o3, o4 = st.columns(4)


    with o1:

        st.metric(
            "Merchant Orders",
            f"{total_orders:,}",
        )


    with o2:

        st.metric(
            "Verified Orders",
            f"{verified_orders:,}",
        )


    with o3:

        st.metric(
            "Pending Orders",
            f"{pending_orders:,}",
        )


    with o4:

        st.metric(
            "Order Value",
            format_inr(
                order_value
            ),
        )


    if merchant_orders:

        order_snapshot_df = pd.DataFrame(
            merchant_orders[:10]
        )


        snapshot_columns = [
            "order_id",
            "customer_name",
            "product_name",
            "quantity",
            "amount",
            "status",
            "payment_id",
        ]


        snapshot_columns = [
            column
            for column in snapshot_columns
            if column in order_snapshot_df.columns
        ]


        st.dataframe(
            order_snapshot_df[
                snapshot_columns
            ],
            use_container_width=True,
            height=300,
            hide_index=True,
        )

    else:

        st.info(
            "No merchant orders have been created yet."
        )


    st.divider()


    # ========================================================
    # HOW MERCHANTOPS THINKS
    # ========================================================

    st.markdown(
        "### 🧠 How MerchantOps AI Makes a Decision"
    )

    st.code(
        """
FAILED PAYMENT
      ↓
Failure Signals
      ↓
Revenue Opportunity
      ↓
Risk Score
      ↓
Recovery Simulation
      ↓
AI Recommendation
      ↓
Governance Guardrails
      ↓
┌───────────────────────────────┐
│ Allowed                       │
│ Merchant Approval Required    │
│ Blocked                       │
└───────────────────────────────┘
      ↓
Merchant Decision
""",
        language="text",
    )

    st.caption(
        "AI recommendations are decision-support outputs. "
        "Governance controls determine whether an action may proceed."
    )

# ============================================================
# TAB 2 — CREATE ORDER
# ============================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">'
        "💰 Create Merchant Order"
        "</div>",
        unsafe_allow_html=True,
    )

    st.info(
        "The merchant controls the product, quantity, "
        "pricing, discount and tax. The backend validates "
        "the final amount and creates the authoritative "
        "Razorpay order."
    )

    with st.form(
        "merchant_order_form",
        clear_on_submit=False,
    ):

        st.markdown("### 👤 Customer")

        c1, c2 = st.columns(2)

        with c1:
            customer_name = st.text_input(
                "Customer Name",
                placeholder="Rahul Sharma",
            )

        with c2:
            customer_email = st.text_input(
                "Customer Email",
                placeholder="rahul@example.com",
            )

        customer_phone = st.text_input(
            "Customer Phone",
            placeholder="+919876543210",
        )

        st.markdown("### 🛍️ Product")

        product_name = st.text_input(
            "Product",
            placeholder="Laptop Backpack",
        )

        description = st.text_area(
            "Description",
            placeholder="Laptop Backpack - Black",
        )

        p1, p2, p3 = st.columns(3)

        with p1:
            quantity = st.number_input(
                "Quantity",
                min_value=1,
                max_value=1000,
                value=1,
                step=1,
            )

        with p2:
            unit_price = st.number_input(
                "Unit Price (₹)",
                min_value=0.01,
                max_value=10000000.00,
                value=1499.00,
                step=1.00,
            )

        with p3:
            discount = st.number_input(
                "Discount (₹)",
                min_value=0.00,
                max_value=10000000.00,
                value=0.00,
                step=1.00,
            )

        tax = st.number_input(
            "Tax (₹)",
            min_value=0.00,
            max_value=10000000.00,
            value=0.00,
            step=1.00,
        )

        subtotal_preview = (
            float(quantity)
            * float(unit_price)
        )

        total_preview = (
            subtotal_preview
            - float(discount)
            + float(tax)
        )

        st.divider()

        st.metric(
            "Merchant-Controlled Total",
            format_inr(
                max(
                    total_preview,
                    0.0,
                )
            ),
        )

        create_order_clicked = st.form_submit_button(
            "💳 Create Razorpay Order",
            use_container_width=True,
            type="primary",
        )

    if create_order_clicked:

        errors = []

        if not customer_name.strip():
            errors.append(
                "Customer name is required."
            )

        if not customer_email.strip():
            errors.append(
                "Customer email is required."
            )
        elif "@" not in customer_email:
            errors.append(
                "Please enter a valid customer email."
            )

        if not customer_phone.strip():
            errors.append(
                "Customer phone is required."
            )

        if not product_name.strip():
            errors.append(
                "Product name is required."
            )

        if total_preview <= 0:
            errors.append(
                "Final amount must be greater than zero."
            )

        if errors:
            for message in errors:
                st.error(
                    message
                )
        else:

            final_description = (
                description.strip()
                if description.strip()
                else product_name.strip()
            )

            payload = {
                "amount": round(
                    total_preview,
                    2,
                ),
                "currency": "INR",
                "customer_name":
                    customer_name.strip(),
                "customer_email":
                    customer_email.strip(),
                "customer_phone":
                    customer_phone.strip(),
                "product_name":
                    product_name.strip(),
                "quantity":
                    int(quantity),
                "unit_price":
                    round(
                        float(unit_price),
                        2,
                    ),
                "subtotal":
                    round(
                        subtotal_preview,
                        2,
                    ),
                "discount":
                    round(
                        float(discount),
                        2,
                    ),
                "tax":
                    round(
                        float(tax),
                        2,
                    ),
                "description":
                    final_description,
            }

            with st.spinner(
                "Creating Razorpay order..."
            ):

                try:

                    created_order = post_api(
                        "/razorpay/create-order",
                        payload,
                    )

                    st.session_state[
                        "last_created_order"
                    ] = created_order

                    st.cache_data.clear()

                    st.success(
                        "Razorpay order created successfully."
                    )

                except Exception as exc:

                    st.error(
                        "Unable to create Razorpay order."
                    )

                    st.code(
                        str(exc)
                    )

    created_order = st.session_state.get(
        "last_created_order"
    )

    if created_order:

        st.divider()

        st.markdown(
            "### ✅ Latest Created Order"
        )

        order_id = created_order.get(
            "order_id"
        )

        amount_paise = safe_int(
            created_order.get(
                "amount",
                0,
            )
        )

        customer = (
            created_order.get(
                "customer",
                {},
            )
            or {}
        )

        commercial_order = (
            created_order.get(
                "order",
                {},
            )
            or {}
        )

        c1, c2, c3 = st.columns(3)

        with c1:
            st.metric(
                "Order ID",
                order_id or "-",
            )

        with c2:
            st.metric(
                "Amount",
                format_inr(
                    amount_paise / 100
                ),
            )

        with c3:
            st.metric(
                "Status",
                created_order.get(
                    "status",
                    "CREATED",
                ),
            )

        st.write(
            f"**Customer:** "
            f"{customer.get('name') or '-'}"
        )

        st.write(
            f"**Email:** "
            f"{customer.get('email') or '-'}"
        )

        st.write(
            f"**Phone:** "
            f"{customer.get('phone') or '-'}"
        )

        st.markdown(
            "#### Commercial Breakdown"
        )

        breakdown_df = pd.DataFrame(
            [
                {
                    "Product":
                        commercial_order.get(
                            "product_name"
                        ),
                    "Quantity":
                        commercial_order.get(
                            "quantity"
                        ),
                    "Unit Price":
                        format_inr(
                            commercial_order.get(
                                "unit_price"
                            )
                        ),
                    "Subtotal":
                        format_inr(
                            commercial_order.get(
                                "subtotal"
                            )
                        ),
                    "Discount":
                        format_inr(
                            commercial_order.get(
                                "discount"
                            )
                        ),
                    "Tax":
                        format_inr(
                            commercial_order.get(
                                "tax"
                            )
                        ),
                    "Final Amount":
                        format_inr(
                            commercial_order.get(
                                "final_amount"
                            )
                        ),
                }
            ]
        )

        st.dataframe(
            breakdown_df,
            use_container_width=True,
            hide_index=True,
        )

        if order_id:

            checkout_link = (
                f"{CHECKOUT_URL}"
                f"?order_id={order_id}"
                f"&api="
                f"{'production' if 'onrender.com' in API_URL else 'local'}"
            )

            st.link_button(
                "💳 Open Customer Checkout",
                checkout_link,
                use_container_width=True,
            )

        with st.expander(
            "View complete create-order response"
        ):
            st.json(
                created_order
            )

# ============================================================
# TAB 3 — PAYMENTS
# ============================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">'
        "💳 Payment Operations"
        "</div>",
        unsafe_allow_html=True,
    )

    st.caption(
        "Search and inspect merchant orders, verified payments, "
        "customer details, payment state, and server-side events."
    )


    # ========================================================
    # REFRESH
    # ========================================================

    if st.button(
        "🔄 Refresh Orders & Payments",
        key="refresh_payment_data",
    ):

        st.cache_data.clear()

        st.rerun()


    # ========================================================
    # VIEW SELECTOR
    # ========================================================

    payment_view = st.radio(
        "View",
        [
            "Merchant Orders",
            "Verified Razorpay Payments",
        ],
        horizontal=True,
        key="payment_view",
    )


    # ========================================================
    # MERCHANT ORDERS
    # ========================================================

    if payment_view == "Merchant Orders":

        if not merchant_orders:

            st.info(
                "No merchant orders found in the active database."
            )

        else:

            orders_df = pd.DataFrame(
                merchant_orders
            ).copy()


            # ------------------------------------------------
            # ENSURE EXPECTED COLUMNS
            # ------------------------------------------------

            expected_columns = [
                "order_id",
                "customer_name",
                "customer_email",
                "customer_phone",
                "product_name",
                "quantity",
                "unit_price",
                "subtotal",
                "discount",
                "tax",
                "amount",
                "currency",
                "description",
                "status",
                "payment_id",
                "created_at",
                "updated_at",
            ]


            for column in expected_columns:

                if column not in orders_df.columns:

                    orders_df[column] = None


            orders_df["status"] = (
                orders_df["status"]
                .fillna("UNKNOWN")
                .astype(str)
                .str.upper()
            )


            # ====================================================
            # SEARCH
            # ====================================================

            st.markdown(
                "### 🔎 Universal Order Search"
            )

            st.caption(
                "Search by Order ID, Payment ID, customer name, "
                "email, phone, product, description or status."
            )


            search_term = st.text_input(
                "Search",
                placeholder=(
                    "order_TWQpB8ZMojpNPi "
                    "or pay_... "
                    "or Rahul "
                    "or Laptop Backpack"
                ),
                key="merchant_order_search",
                label_visibility="collapsed",
            ).strip().lower()


            # ====================================================
            # FILTERS
            # ====================================================

            filter_col1, filter_col2, filter_col3 = st.columns(
                3
            )


            with filter_col1:

                status_options = [
                    "ALL",
                    *sorted(
                        orders_df[
                            "status"
                        ]
                        .dropna()
                        .astype(str)
                        .unique()
                        .tolist()
                    ),
                ]


                selected_status = st.selectbox(
                    "Status",
                    status_options,
                    key="merchant_order_status_filter",
                )


            with filter_col2:

                payment_state_options = [
                    "ALL",
                    "PAID",
                    "UNPAID",
                ]


                selected_payment_state = st.selectbox(
                    "Payment State",
                    payment_state_options,
                    key="merchant_payment_state_filter",
                )


            with filter_col3:

                min_amount = st.number_input(
                    "Minimum Amount (₹)",
                    min_value=0.0,
                    value=0.0,
                    step=100.0,
                    key="merchant_min_amount_filter",
                )


            # ====================================================
            # APPLY FILTERS
            # ====================================================

            filtered_orders = orders_df.copy()


            if search_term:

                searchable_columns = [
                    "order_id",
                    "customer_name",
                    "customer_email",
                    "customer_phone",
                    "product_name",
                    "payment_id",
                    "description",
                    "status",
                ]


                mask = pd.Series(
                    False,
                    index=filtered_orders.index,
                )


                for column in searchable_columns:

                    values = (
                        filtered_orders[column]
                        .fillna("")
                        .astype(str)
                        .str.lower()
                    )


                    mask = (
                        mask
                        |
                        values.str.contains(
                            search_term,
                            regex=False,
                            na=False,
                        )
                    )


                filtered_orders = (
                    filtered_orders[
                        mask
                    ]
                )


            if selected_status != "ALL":

                filtered_orders = (
                    filtered_orders[
                        filtered_orders[
                            "status"
                        ]
                        ==
                        selected_status
                    ]
                )


            if selected_payment_state == "PAID":

                filtered_orders = (
                    filtered_orders[
                        filtered_orders[
                            "payment_id"
                        ]
                        .notna()
                        &
                        (
                            filtered_orders[
                                "payment_id"
                            ]
                            .astype(str)
                            .str.strip()
                            !=
                            ""
                        )
                    ]
                )


            elif selected_payment_state == "UNPAID":

                filtered_orders = (
                    filtered_orders[
                        filtered_orders[
                            "payment_id"
                        ]
                        .isna()
                    ]
                )


            filtered_orders["amount_numeric"] = (
                pd.to_numeric(
                    filtered_orders[
                        "amount"
                    ],
                    errors="coerce",
                )
                .fillna(0)
            )


            filtered_orders = (
                filtered_orders[
                    filtered_orders[
                        "amount_numeric"
                    ]
                    >=
                    float(
                        min_amount
                    )
                ]
            )


            # ====================================================
            # ORDER METRICS
            # ====================================================

            total_orders = len(
                orders_df
            )

            matching_orders = len(
                filtered_orders
            )

            verified_orders = int(
                (
                    filtered_orders[
                        "status"
                    ]
                    ==
                    "VERIFIED"
                ).sum()
            )

            pending_orders = int(
                (
                    filtered_orders[
                        "status"
                    ]
                    ==
                    "CREATED"
                ).sum()
            )

            failed_orders = int(
                (
                    filtered_orders[
                        "status"
                    ]
                    ==
                    "FAILED"
                ).sum()
            )

            visible_order_value = float(
                filtered_orders[
                    "amount_numeric"
                ].sum()
            )


            om1, om2, om3, om4, om5 = st.columns(
                5
            )


            with om1:

                st.metric(
                    "Total Orders",
                    f"{total_orders:,}",
                )


            with om2:

                st.metric(
                    "Matching",
                    f"{matching_orders:,}",
                )


            with om3:

                st.metric(
                    "Verified",
                    f"{verified_orders:,}",
                )


            with om4:

                st.metric(
                    "Pending",
                    f"{pending_orders:,}",
                )


            with om5:

                st.metric(
                    "Visible Value",
                    format_inr(
                        visible_order_value
                    ),
                )


            if failed_orders > 0:

                st.warning(
                    f"{failed_orders:,} filtered order(s) are marked as FAILED."
                )


            st.divider()


            # ====================================================
            # DOWNLOAD
            # ====================================================

            download_df = (
                filtered_orders
                .drop(
                    columns=[
                        "amount_numeric"
                    ],
                    errors="ignore",
                )
                .copy()
            )


            st.download_button(
                "📥 Download Filtered Orders",
                data=download_df.to_csv(
                    index=False
                ),
                file_name="merchant_orders_filtered.csv",
                mime="text/csv",
                key="download_filtered_orders",
            )


            # ====================================================
            # ORDER TABLE
            # ====================================================

            st.markdown(
                "### 🧾 Merchant Orders"
            )


            display_columns = [
                "order_id",
                "customer_name",
                "product_name",
                "quantity",
                "amount",
                "currency",
                "status",
                "payment_id",
                "created_at",
            ]


            display_columns = [
                column
                for column
                in display_columns
                if column
                in filtered_orders.columns
            ]


            if filtered_orders.empty:

                st.warning(
                    "No orders match the current search and filters."
                )

            else:

                st.dataframe(
                    filtered_orders[
                        display_columns
                    ],
                    use_container_width=True,
                    height=520,
                    hide_index=True,
                )


            st.divider()


            # ====================================================
            # EXACT ORDER LOOKUP
            # ====================================================

            st.markdown(
                "### 🔎 Exact Order Lookup"
            )

            st.caption(
                "This queries the server directly. "
                "It is better than browser Ctrl+F for large datasets."
            )


            exact_order_id = st.text_input(
                "Order ID",
                value=st.session_state.get(
                    "loaded_order_id",
                    "",
                ),
                placeholder="order_TWQpB8ZMojpNPi",
                key="exact_order_id_input",
            ).strip()


            load_order = st.button(
                "📄 Load Complete Order",
                key="load_exact_order",
                type="primary",
                use_container_width=True,
            )


            if load_order:

                if not exact_order_id:

                    st.warning(
                        "Enter an Order ID first."
                    )

                else:

                    st.session_state[
                        "loaded_order_id"
                    ] = exact_order_id


            loaded_order_id = (
                st.session_state.get(
                    "loaded_order_id"
                )
                or
                ""
            )


            if loaded_order_id:

                try:

                    exact_order_response = fetch_api(
                        f"/merchant/orders/"
                        f"{loaded_order_id}"
                    )


                    selected_order = (
                        exact_order_response.get(
                            "order"
                        )
                    )


                except Exception as exc:

                    selected_order = None

                    st.error(
                        "Unable to load the selected order."
                    )

                    st.code(
                        str(exc)
                    )


                if selected_order:

                    selected_status = (
                        normalize_status(
                            selected_order.get(
                                "status"
                            )
                        )
                    )


                    st.divider()


                    st.markdown(
                        "## 🧾 Complete Order Details"
                    )


                    # --------------------------------------------
                    # ORDER HEADER
                    # --------------------------------------------

                    d1, d2, d3, d4 = st.columns(
                        4
                    )


                    with d1:

                        st.metric(
                            "Amount",
                            format_inr(
                                selected_order.get(
                                    "amount"
                                )
                            ),
                        )


                    with d2:

                        st.metric(
                            "Status",
                            selected_status,
                        )


                    with d3:

                        st.metric(
                            "Order ID",
                            selected_order.get(
                                "order_id"
                            )
                            or
                            "-",
                        )


                    with d4:

                        st.metric(
                            "Payment ID",
                            selected_order.get(
                                "payment_id"
                            )
                            or
                            "Not Paid",
                        )


                    # --------------------------------------------
                    # STATUS MESSAGE
                    # --------------------------------------------

                    if selected_status == "VERIFIED":

                        st.success(
                            "🟢 Payment verified successfully."
                        )

                    elif selected_status == "CAPTURED":

                        st.success(
                            "🟢 Payment captured successfully."
                        )

                    elif selected_status == "FAILED":

                        st.error(
                            "🔴 Payment failed."
                        )

                    elif selected_status == "CREATED":

                        st.info(
                            "⏳ Order created. Payment has not been completed."
                        )

                    else:

                        st.warning(
                            f"Current order status: {selected_status}"
                        )


                    # --------------------------------------------
                    # CUSTOMER
                    # --------------------------------------------

                    st.markdown(
                        "### 👤 Customer"
                    )


                    customer_col1, customer_col2, customer_col3 = (
                        st.columns(3)
                    )


                    with customer_col1:

                        st.write(
                            "**Name**"
                        )

                        st.write(
                            selected_order.get(
                                "customer_name"
                            )
                            or
                            "-"
                        )


                    with customer_col2:

                        st.write(
                            "**Email**"
                        )

                        st.write(
                            selected_order.get(
                                "customer_email"
                            )
                            or
                            "-"
                        )


                    with customer_col3:

                        st.write(
                            "**Phone**"
                        )

                        st.write(
                            selected_order.get(
                                "customer_phone"
                            )
                            or
                            "-"
                        )


                    # --------------------------------------------
                    # PRODUCT
                    # --------------------------------------------

                    st.markdown(
                        "### 🛍️ Product"
                    )


                    st.write(
                        f"**Product:** "
                        f"{selected_order.get('product_name') or '-'}"
                    )


                    st.write(
                        f"**Description:** "
                        f"{selected_order.get('description') or '-'}"
                    )


                    # --------------------------------------------
                    # PRICE BREAKDOWN
                    # --------------------------------------------

                    st.markdown(
                        "### 💰 Complete Price Breakdown"
                    )


                    price_df = pd.DataFrame(
                        [
                            {
                                "Quantity":
                                    selected_order.get(
                                        "quantity"
                                    ),

                                "Unit Price":
                                    format_inr(
                                        selected_order.get(
                                            "unit_price"
                                        )
                                    ),

                                "Subtotal":
                                    format_inr(
                                        selected_order.get(
                                            "subtotal"
                                        )
                                    ),

                                "Discount":
                                    format_inr(
                                        selected_order.get(
                                            "discount"
                                        )
                                    ),

                                "Tax":
                                    format_inr(
                                        selected_order.get(
                                            "tax"
                                        )
                                    ),

                                "Final Amount":
                                    format_inr(
                                        selected_order.get(
                                            "amount"
                                        )
                                    ),
                            }
                        ]
                    )


                    st.dataframe(
                        price_df,
                        use_container_width=True,
                        hide_index=True,
                    )


                    # --------------------------------------------
                    # PAYMENT DETAILS
                    # --------------------------------------------

                    st.markdown(
                        "### 🔐 Payment Details"
                    )


                    payment_id = (
                        selected_order.get(
                            "payment_id"
                        )
                    )


                    related_payment = None


                    if payment_id:

                        related_payment = next(
                            (
                                payment
                                for payment
                                in verified_payments
                                if str(
                                    payment.get(
                                        "payment_id"
                                    )
                                )
                                ==
                                str(
                                    payment_id
                                )
                            ),
                            None,
                        )


                    if related_payment:

                        payment_details_df = pd.DataFrame(
                            [
                                {
                                    "Payment ID":
                                        related_payment.get(
                                            "payment_id"
                                        ),

                                    "Order ID":
                                        related_payment.get(
                                            "order_id"
                                        ),

                                    "Amount":
                                        format_inr(
                                            related_payment.get(
                                                "amount"
                                            )
                                        ),

                                    "Currency":
                                        related_payment.get(
                                            "currency"
                                        ),

                                    "Method":
                                        related_payment.get(
                                            "payment_method"
                                        ),

                                    "Payment Status":
                                        related_payment.get(
                                            "payment_status"
                                        ),

                                    "Captured":
                                        (
                                            "YES"
                                            if related_payment.get(
                                                "captured"
                                            )
                                            else
                                            "NO"
                                        ),

                                    "Refunded":
                                        format_inr(
                                            related_payment.get(
                                                "amount_refunded"
                                            )
                                        ),

                                    "Email":
                                        related_payment.get(
                                            "email"
                                        ),

                                    "Contact":
                                        related_payment.get(
                                            "contact"
                                        ),
                                }
                            ]
                        )


                        st.dataframe(
                            payment_details_df,
                            use_container_width=True,
                            hide_index=True,
                        )


                    else:

                        st.info(
                            "No verified payment is linked to this order yet."
                        )


                    # --------------------------------------------
                    # WEBHOOK TIMELINE
                    # --------------------------------------------

                    st.markdown(
                        "### ⏱️ Payment Timeline"
                    )


                    related_webhooks = [

                        event

                        for event
                        in webhook_events

                        if payment_id

                        and str(
                            event.get(
                                "payment_id"
                            )
                        )
                        ==
                        str(
                            payment_id
                        )
                    ]


                    timeline = [

                        (
                            "Merchant Order Created",
                            True,
                        ),

                        (
                            "Razorpay Order Created",
                            True,
                        ),

                        (
                            "Customer Payment",
                            bool(
                                payment_id
                            ),
                        ),

                        (
                            "Signature Verification",
                            bool(
                                related_payment
                            ),
                        ),

                        (
                            "Webhook Received",
                            bool(
                                related_webhooks
                            ),
                        ),

                        (
                            "Merchant Order Updated",
                            selected_status
                            in {
                                "AUTHORIZED",
                                "CAPTURED",
                                "VERIFIED",
                                "FAILED",
                            },
                        ),

                    ]


                    for label, complete in timeline:

                        st.write(
                            (
                                "✅"
                                if complete
                                else
                                "⏳"
                            )
                            +
                            f" **{label}**"
                        )


                    # --------------------------------------------
                    # WEBHOOK EVENTS
                    # --------------------------------------------

                    if related_webhooks:

                        st.markdown(
                            "### 🔔 Related Webhook Events"
                        )


                        st.dataframe(
                            pd.DataFrame(
                                related_webhooks
                            ),
                            use_container_width=True,
                            height=320,
                            hide_index=True,
                        )


                    # --------------------------------------------
                    # ORDER DATES
                    # --------------------------------------------

                    st.markdown(
                        "### 📅 Order Timestamps"
                    )


                    timestamps_df = pd.DataFrame(
                        [
                            {
                                "Created At":
                                    selected_order.get(
                                        "created_at"
                                    ),

                                "Updated At":
                                    selected_order.get(
                                        "updated_at"
                                    ),

                            }
                        ]
                    )


                    st.dataframe(
                        timestamps_df,
                        use_container_width=True,
                        hide_index=True,
                    )


                    # --------------------------------------------
                    # RAW JSON
                    # --------------------------------------------

                    with st.expander(
                        "🔍 View Complete Server Order JSON"
                    ):

                        st.json(
                            selected_order
                        )


                elif load_order:

                    st.error(
                        "❌ Order not found."
                    )


    # ========================================================
    # VERIFIED PAYMENTS VIEW
    # ========================================================

    else:

        st.markdown(
            "### ✅ Verified Razorpay Payments"
        )


        if not verified_payments:

            st.info(
                "No verified Razorpay payments found."
            )

        else:

            verified_df = pd.DataFrame(
                verified_payments
            ).copy()


            verified_search = st.text_input(
                "🔎 Search Payment ID, Order ID, Email, Contact or Method",
                placeholder="pay_... / order_...",
                key="verified_payment_search",
            ).strip().lower()


            if verified_search:

                search_columns = [

                    column

                    for column

                    in [
                        "payment_id",
                        "order_id",
                        "email",
                        "contact",
                        "payment_status",
                        "payment_method",
                    ]

                    if column
                    in verified_df.columns
                ]


                mask = pd.Series(
                    False,
                    index=verified_df.index,
                )


                for column in search_columns:

                    values = (
                        verified_df[column]
                        .fillna("")
                        .astype(str)
                        .str.lower()
                    )


                    mask = (
                        mask
                        |
                        values.str.contains(
                            verified_search,
                            regex=False,
                            na=False,
                        )
                    )


                verified_df = (
                    verified_df[
                        mask
                    ]
                )


            v1, v2, v3 = st.columns(3)


            with v1:

                st.metric(
                    "Verified Payments",
                    len(
                        verified_df
                    ),
                )


            with v2:

                st.metric(
                    "Total Verified Value",
                    format_inr(
                        pd.to_numeric(
                            verified_df.get(
                                "amount",
                                pd.Series(
                                    dtype=float
                                )
                            ),
                            errors="coerce",
                        )
                        .fillna(0)
                        .sum()
                    ),
                )


            with v3:

                st.metric(
                    "Matching Results",
                    len(
                        verified_df
                    ),
                )


            st.download_button(
                "📥 Download Verified Payments",
                data=verified_df.to_csv(
                    index=False
                ),
                file_name="verified_payments.csv",
                mime="text/csv",
                key="download_verified_payments",
            )


            st.dataframe(
                verified_df,
                use_container_width=True,
                height=600,
                hide_index=True,
            )

# ============================================================
# TAB 4 — AI RECOVERY
# ============================================================

with tabs[3]:

    st.markdown(
        '<div class="section-title">'
        "🤖 AI Recovery & Decision Intelligence"
        "</div>",
        unsafe_allow_html=True,
    )

    st.caption(
        "Explainable recovery decisions generated from "
        "failure signals, risk scoring, simulation and governance."
    )

    # ========================================================
    # NO DECISIONS
    # ========================================================

    if not decision_records:

        st.info(
            "No AI recovery decisions are currently available."
        )

    else:

        # ====================================================
        # BUILD DECISION TABLE
        # ====================================================

        recovery_rows = []

        for decision in decision_records:

            policy = (
                decision.get(
                    "policy",
                    {},
                )
                or {}
            )

            recovery_rows.append(
                {
                    "Payment ID":
                        decision.get(
                            "payment_id"
                        ),

                    "Order ID":
                        decision.get(
                            "order_id"
                        ),

                    "Amount":
                        safe_float(
                            decision.get(
                                "amount"
                            )
                        ),

                    "Failure Reason":
                        decision.get(
                            "failure_reason"
                        ),

                    "Risk Score":
                        safe_float(
                            decision.get(
                                "risk_score"
                            )
                        ),

                    "Risk Level":
                        normalize_status(
                            decision.get(
                                "risk_level"
                            )
                        ),

                    "Recovery Probability":
                        safe_float(
                            decision.get(
                                "recovery_probability"
                            )
                        ),

                    "Expected Recovery":
                        safe_float(
                            decision.get(
                                "expected_recovery"
                            )
                        ),

                    "AI Recommendation":
                        normalize_status(
                            decision.get(
                                "recommended_action"
                            )
                        ),

                    "Final Action":
                        normalize_status(
                            decision.get(
                                "final_action"
                            )
                        ),

                    "Approval Required":
                        (
                            "YES"
                            if decision.get(
                                "approval_required"
                            )
                            else
                            "NO"
                        ),

                    "Execution Mode":
                        policy.get(
                            "execution_mode"
                        )
                        or
                        "-",

                    "Policy Allowed":
                        (
                            "YES"
                            if policy.get(
                                "allowed"
                            )
                            else
                            "NO"
                        ),
                }
            )

        recovery_df = pd.DataFrame(
            recovery_rows
        )


        # ====================================================
        # FILTER BAR
        # ====================================================

        st.markdown(
            "### 🔎 Recovery Decision Explorer"
        )

        filter1, filter2, filter3, filter4 = st.columns(4)


        with filter1:

            action_filter = st.selectbox(
                "Final Action",
                [
                    "ALL",
                    "RETRY_NOW",
                    "RETRY_LATER",
                    "REVIEW",
                    "DO_NOTHING",
                ],
                key="ai_final_action_filter",
            )


        with filter2:

            risk_filter = st.selectbox(
                "Risk Level",
                [
                    "ALL",
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                ],
                key="ai_risk_filter",
            )


        with filter3:

            approval_filter = st.selectbox(
                "Approval",
                [
                    "ALL",
                    "REQUIRED",
                    "NOT_REQUIRED",
                ],
                key="ai_approval_filter",
            )


        with filter4:

            minimum_recovery = st.number_input(
                "Minimum Expected Recovery (₹)",
                min_value=0.0,
                value=0.0,
                step=50.0,
                key="ai_min_recovery_filter",
            )


        filtered_df = recovery_df.copy()


        if action_filter != "ALL":

            filtered_df = filtered_df[
                filtered_df[
                    "Final Action"
                ]
                ==
                action_filter
            ]


        if risk_filter != "ALL":

            filtered_df = filtered_df[
                filtered_df[
                    "Risk Level"
                ]
                ==
                risk_filter
            ]


        if approval_filter == "REQUIRED":

            filtered_df = filtered_df[
                filtered_df[
                    "Approval Required"
                ]
                ==
                "YES"
            ]


        elif approval_filter == "NOT_REQUIRED":

            filtered_df = filtered_df[
                filtered_df[
                    "Approval Required"
                ]
                ==
                "NO"
            ]


        filtered_df = filtered_df[
            filtered_df[
                "Expected Recovery"
            ]
            >=
            minimum_recovery
        ]


        # ====================================================
        # SUMMARY METRICS
        # ====================================================

        ai_count = len(
            filtered_df
        )

        high_risk_count = int(
            (
                filtered_df[
                    "Risk Level"
                ]
                ==
                "HIGH"
            ).sum()
        )

        approval_count = int(
            (
                filtered_df[
                    "Approval Required"
                ]
                ==
                "YES"
            ).sum()
        )

        blocked_count = int(
            (
                filtered_df[
                    "Policy Allowed"
                ]
                ==
                "NO"
            ).sum()
        )

        expected_recovery_total = safe_float(
            filtered_df[
                "Expected Recovery"
            ]
            .fillna(0)
            .sum()
        )


        s1, s2, s3, s4, s5 = st.columns(5)


        with s1:

            st.metric(
                "AI Decisions",
                ai_count,
            )


        with s2:

            st.metric(
                "High Risk",
                high_risk_count,
            )


        with s3:

            st.metric(
                "Approval Required",
                approval_count,
            )


        with s4:

            st.metric(
                "Blocked",
                blocked_count,
            )


        with s5:

            st.metric(
                "Expected Recovery",
                format_inr(
                    expected_recovery_total
                ),
            )


        st.divider()


        # ====================================================
        # DECISION TABLE
        # ====================================================

        st.markdown(
            "### 📊 AI Recovery Decisions"
        )


        if filtered_df.empty:

            st.warning(
                "No decisions match the selected filters."
            )

        else:

            table_df = filtered_df.copy()

            table_df[
                "Amount"
            ] = table_df[
                "Amount"
            ].apply(
                format_inr
            )

            table_df[
                "Expected Recovery"
            ] = table_df[
                "Expected Recovery"
            ].apply(
                format_inr
            )

            table_df[
                "Recovery Probability"
            ] = table_df[
                "Recovery Probability"
            ].apply(
                lambda value:
                    f"{value * 100:.1f}%"
            )

            st.dataframe(
                table_df,
                use_container_width=True,
                height=500,
                hide_index=True,
            )


        st.download_button(
            "📥 Download AI Recovery Decisions",
            data=
                filtered_df.to_csv(
                    index=False
                ),
            file_name=
                "merchantops_ai_recovery.csv",
            mime=
                "text/csv",
            key=
                "download_ai_recovery",
        )


        st.divider()


        # ====================================================
        # PAYMENT EXPLAINABILITY
        # ====================================================

        st.markdown(
            "### 🧠 Decision Explainability"
        )

        payment_options = [

            str(
                decision.get(
                    "payment_id"
                )
            )

            for decision
            in decision_records

            if decision.get(
                "payment_id"
            )

        ]


        if not payment_options:

            st.info(
                "No payment IDs are available for explainability."
            )

        else:

            selected_payment = st.selectbox(
                "Select Failed Payment",
                payment_options,
                key="ai_explainability_payment",
            )


            selected_decision = next(

                (
                    decision
                    for decision
                    in decision_records
                    if str(
                        decision.get(
                            "payment_id"
                        )
                    )
                    ==
                    selected_payment
                ),

                None,
            )


            if selected_decision:

                policy = (
                    selected_decision.get(
                        "policy",
                        {},
                    )
                    or {}
                )


                # ==================================================
                # CORE VALUES
                # ==================================================

                amount = safe_float(
                    selected_decision.get(
                        "amount"
                    )
                )

                risk_score = safe_float(
                    selected_decision.get(
                        "risk_score"
                    )
                )

                recovery_probability = safe_float(
                    selected_decision.get(
                        "recovery_probability"
                    )
                )

                expected_recovery = safe_float(
                    selected_decision.get(
                        "expected_recovery"
                    )
                )

                decision_confidence = safe_float(
                    selected_decision.get(
                        "decision_confidence"
                    )
                )

                risk_level = normalize_status(
                    selected_decision.get(
                        "risk_level"
                    )
                )

                recommended_action = normalize_status(
                    selected_decision.get(
                        "recommended_action"
                    )
                )

                final_action = normalize_status(
                    selected_decision.get(
                        "final_action"
                    )
                )

                approval_required = bool(
                    selected_decision.get(
                        "approval_required"
                    )
                )

                allowed = bool(
                    policy.get(
                        "allowed",
                        False,
                    )
                )

                execution_mode = (
                    policy.get(
                        "execution_mode"
                    )
                    or
                    "UNKNOWN"
                )


                # ==================================================
                # TOP SUMMARY
                # ==================================================

                st.markdown(
                    "#### 🔴 Payment Failure Analysis"
                )


                d1, d2, d3, d4 = st.columns(4)


                with d1:

                    st.metric(
                        "Failed Amount",
                        format_inr(
                            amount
                        ),
                    )


                with d2:

                    st.metric(
                        "Risk Score",
                        f"{risk_score:.2f}",
                    )


                with d3:

                    st.metric(
                        "Recovery Probability",
                        f"{recovery_probability * 100:.1f}%",
                    )


                with d4:

                    st.metric(
                        "Expected Recovery",
                        format_inr(
                            expected_recovery
                        ),
                    )


                # ==================================================
                # RISK LEVEL
                # ==================================================

                if risk_level == "HIGH":

                    st.error(
                        f"🔴 HIGH RISK — Risk Score {risk_score:.2f}"
                    )

                elif risk_level == "MEDIUM":

                    st.warning(
                        f"🟠 MEDIUM RISK — Risk Score {risk_score:.2f}"
                    )

                elif risk_level == "LOW":

                    st.success(
                        f"🟢 LOW RISK — Risk Score {risk_score:.2f}"
                    )

                else:

                    st.info(
                        f"Risk Level: {risk_level}"
                    )


                st.divider()


                # ==================================================
                # PAYMENT INFORMATION
                # ==================================================

                st.markdown(
                    "#### 💳 Payment Information"
                )


                info_left, info_right = st.columns(2)


                with info_left:

                    st.write(
                        f"**Payment ID:** "
                        f"{selected_decision.get('payment_id') or '-'}"
                    )

                    st.write(
                        f"**Order ID:** "
                        f"{selected_decision.get('order_id') or '-'}"
                    )

                    st.write(
                        f"**Customer:** "
                        f"{selected_decision.get('customer_id') or '-'}"
                    )

                    st.write(
                        f"**Payment Method:** "
                        f"{selected_decision.get('payment_method') or '-'}"
                    )


                with info_right:

                    st.write(
                        f"**Failure Reason:** "
                        f"{selected_decision.get('failure_reason') or '-'}"
                    )

                    st.write(
                        f"**Error Code:** "
                        f"{selected_decision.get('error_code') or '-'}"
                    )

                    st.write(
                        f"**Error Source:** "
                        f"{selected_decision.get('error_source') or '-'}"
                    )

                    st.write(
                        f"**Error Step:** "
                        f"{selected_decision.get('error_step') or '-'}"
                    )


                st.divider()


                # ==================================================
                # WHY AI CHOSE THIS
                # ==================================================

                st.markdown(
                    "#### 💡 Why did the AI choose this?"
                )


                decision_reason = (
                    selected_decision.get(
                        "decision_reason"
                    )
                    or
                    "No decision explanation was provided."
                )


                st.info(
                    decision_reason
                )


                # ==================================================
                # AI RECOMMENDATION VS FINAL DECISION
                # ==================================================

                st.markdown(
                    "#### 🎯 AI Recommendation"
                )


                recommendation_col1, recommendation_col2 = (
                    st.columns(2)
                )


                with recommendation_col1:

                    st.write(
                        "**Agent Recommendation**"
                    )


                    if recommended_action == "RETRY_NOW":

                        st.success(
                            "🟢 RETRY_NOW"
                        )

                    elif recommended_action == "RETRY_LATER":

                        st.warning(
                            "🟡 RETRY_LATER"
                        )

                    elif recommended_action == "REVIEW":

                        st.warning(
                            "🟠 REVIEW"
                        )

                    elif recommended_action == "DO_NOTHING":

                        st.error(
                            "🔴 DO_NOTHING"
                        )

                    else:

                        st.info(
                            recommended_action
                            or
                            "UNKNOWN"
                        )


                with recommendation_col2:

                    st.write(
                        "**Final Governed Action**"
                    )


                    if final_action == "RETRY_NOW":

                        st.success(
                            "🟢 RETRY_NOW"
                        )

                    elif final_action == "RETRY_LATER":

                        st.warning(
                            "🟡 RETRY_LATER"
                        )

                    elif final_action == "REVIEW":

                        st.warning(
                            "🟠 REVIEW"
                        )

                    elif final_action == "DO_NOTHING":

                        st.error(
                            "🔴 DO_NOTHING"
                        )

                    else:

                        st.info(
                            final_action
                        )


                st.caption(
                    "The AI recommendation is not automatically executed. "
                    "Governance determines whether the final action can proceed."
                )


                # ==================================================
                # GOVERNANCE
                # ==================================================

                st.markdown(
                    "#### 🛡️ Governance Decision"
                )


                gov1, gov2, gov3 = st.columns(3)


                with gov1:

                    if allowed:

                        st.success(
                            "✅ ACTION ALLOWED"
                        )

                    else:

                        st.error(
                            "🚫 ACTION BLOCKED"
                        )


                with gov2:

                    if approval_required:

                        st.warning(
                            "🛡️ MERCHANT APPROVAL REQUIRED"
                        )

                    else:

                        st.info(
                            "No Merchant Approval Required"
                        )


                with gov3:

                    st.metric(
                        "Execution Mode",
                        execution_mode,
                    )


                policy_reason = (
                    policy.get(
                        "reason"
                    )
                    or
                    "No policy explanation available."
                )


                st.info(
                    f"**Governance Policy:** {policy_reason}"
                )


                # ==================================================
                # DECISION CONFIDENCE
                # ==================================================

                st.markdown(
                    "#### 📈 Decision Confidence"
                )


                st.progress(
                    min(
                        max(
                            decision_confidence,
                            0.0,
                        ),
                        1.0,
                    )
                )


                st.write(
                    f"Decision confidence: "
                    f"**{decision_confidence * 100:.1f}%**"
                )


                # ==================================================
                # SIMULATION
                # ==================================================

                st.markdown(
                    "#### 🧪 Recovery Simulation"
                )


                scenarios = (
                    selected_decision.get(
                        "simulation_scenarios",
                        [],
                    )
                    or []
                )


                if scenarios:

                    simulation_rows = []


                    for scenario in scenarios:

                        scenario_probability = safe_float(
                            scenario.get(
                                "probability"
                            )
                        )

                        scenario_recovery = safe_float(
                            scenario.get(
                                "expected_recovery"
                            )
                        )

                        scenario_risk = safe_float(
                            scenario.get(
                                "risk"
                            )
                        )


                        simulation_rows.append(
                            {
                                "Action":
                                    scenario.get(
                                        "action"
                                    ),

                                "Probability":
                                    f"{scenario_probability * 100:.1f}%",

                                "Expected Recovery":
                                    format_inr(
                                        scenario_recovery
                                    ),

                                "Risk":
                                    f"{scenario_risk:.2f}",
                            }
                        )


                    simulation_df = pd.DataFrame(
                        simulation_rows
                    )


                    st.dataframe(
                        simulation_df,
                        use_container_width=True,
                        hide_index=True,
                    )


                    best_scenario = max(
                        scenarios,
                        key=lambda scenario:
                            safe_float(
                                scenario.get(
                                    "expected_recovery"
                                )
                            ),
                    )


                    st.write(
                        "**Highest simulated recovery:** "
                        f"{best_scenario.get('action')} → "
                        f"{format_inr(best_scenario.get('expected_recovery'))}"
                    )


                else:

                    st.info(
                        "No recovery simulation scenarios are available."
                    )


                # ==================================================
                # DECISION SUMMARY
                # ==================================================

                st.markdown(
                    "#### 🧾 Decision Summary"
                )


                summary_df = pd.DataFrame(
                    [
                        {
                            "Payment":
                                selected_decision.get(
                                    "payment_id"
                                ),

                            "Amount":
                                format_inr(
                                    amount
                                ),

                            "Failure":
                                selected_decision.get(
                                    "failure_reason"
                                ),

                            "Risk":
                                risk_level,

                            "Risk Score":
                                f"{risk_score:.2f}",

                            "Recovery Probability":
                                f"{recovery_probability * 100:.1f}%",

                            "Expected Recovery":
                                format_inr(
                                    expected_recovery
                                ),

                            "AI Recommendation":
                                recommended_action,

                            "Final Action":
                                final_action,

                            "Approval":
                                (
                                    "REQUIRED"
                                    if approval_required
                                    else
                                    "NOT REQUIRED"
                                ),

                            "Execution":
                                execution_mode,

                        }
                    ]
                )


                st.dataframe(
                    summary_df,
                    use_container_width=True,
                    hide_index=True,
                )


                # ==================================================
                # RAW JSON
                # ==================================================

                with st.expander(
                    "🔍 View Complete AI Decision JSON"
                ):

                    st.json(
                        selected_decision
                    )


# ============================================================
# TAB 5 — APPROVALS
# ============================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">'
        "🛡️ Merchant Approval Queue"
        "</div>",
        unsafe_allow_html=True,
    )

    approval_rows = []

    for decision in decision_records:

        if not decision.get(
            "approval_required",
            False,
        ):
            continue

        approval_rows.append(
            {
                "Payment ID":
                    decision.get(
                        "payment_id"
                    ),
                "Order ID":
                    decision.get(
                        "order_id"
                    ),
                "Amount":
                    format_inr(
                        decision.get(
                            "amount"
                        )
                    ),
                "Risk":
                    decision.get(
                        "risk_level"
                    ),
                "Expected Recovery":
                    format_inr(
                        decision.get(
                            "expected_recovery"
                        )
                    ),
                "Action":
                    decision.get(
                        "final_action"
                    ),
                "Reason":
                    decision.get(
                        "decision_reason"
                    ),
            }
        )

    if approval_rows:

        st.warning(
            f"{len(approval_rows)} decision(s) require merchant approval."
        )

        st.dataframe(
            pd.DataFrame(
                approval_rows
            ),
            use_container_width=True,
            height=500,
            hide_index=True,
        )

        st.caption(
            "Approval controls are governance/demo controls. "
            "The dashboard does not execute live financial recovery actions."
        )

    else:

        st.success(
            "No merchant approvals currently required."
        )


# ============================================================
# TAB 6 — WEBHOOKS
# ============================================================

with tabs[5]:

    st.markdown(
        '<div class="section-title">'
        "🔔 Razorpay Webhook Activity"
        "</div>",
        unsafe_allow_html=True,
    )

    w1, w2, w3 = st.columns(3)

    with w1:
        st.metric(
            "Webhook Events",
            safe_int(
                activity_data.get(
                    "webhook_events",
                    0,
                )
            ),
        )

    with w2:
        st.metric(
            "Webhook Processing",
            safe_int(
                activity_data.get(
                    "webhook_processing",
                    0,
                )
            ),
        )

    with w3:
        st.metric(
            "Verified Payments",
            safe_int(
                activity_data.get(
                    "verified_payments",
                    0,
                )
            ),
        )

    st.divider()

    if webhook_events:

        webhook_df = pd.DataFrame(
            webhook_events
        )

        webhook_search = st.text_input(
            "🔎 Search webhook events",
            placeholder="payment.captured / payment.failed / pay_...",
            key="webhook_search",
        ).strip().lower()

        if webhook_search:

            mask = pd.Series(
                False,
                index=webhook_df.index,
            )

            for column in webhook_df.columns:

                values = (
                    webhook_df[column]
                    .fillna("")
                    .astype(str)
                    .str.lower()
                )

                mask = (
                    mask
                    |
                    values.str.contains(
                        webhook_search,
                        regex=False,
                        na=False,
                    )
                )

            webhook_df = webhook_df[
                mask
            ]

        st.dataframe(
            webhook_df,
            use_container_width=True,
            height=550,
            hide_index=True,
        )

        st.download_button(
            "📥 Download Webhook Events",
            data=webhook_df.to_csv(
                index=False
            ),
            file_name="webhook_events.csv",
            mime="text/csv",
            key="download_webhook_events",
        )

    else:

        st.info(
            "No Razorpay webhook events found."
        )


# ============================================================
# TAB 7 — AUDIT
# ============================================================

with tabs[6]:

    st.markdown(
        '<div class="section-title">'
        "📋 Audit Trail"
        "</div>",
        unsafe_allow_html=True,
    )

    if audit_events:

        audit_rows = []

        for event in audit_events:

            audit_rows.append(
                {
                    "Timestamp":
                        event.get(
                            "timestamp"
                        ),
                    "Event":
                        event.get(
                            "event_type"
                        ),
                    "Payment":
                        event.get(
                            "payment_id"
                        ),
                    "Decision":
                        event.get(
                            "decision"
                        ),
                    "Action":
                        event.get(
                            "action"
                        ),
                    "Risk":
                        event.get(
                            "risk_level"
                        ),
                    "Approval":
                        event.get(
                            "approval_required"
                        ),
                    "Execution Mode":
                        event.get(
                            "execution_mode"
                        ),
                    "Status":
                        event.get(
                            "status"
                        ),
                }
            )

        audit_df = pd.DataFrame(
            audit_rows
        )

        event_options = sorted(
            audit_df["Event"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        status_options = sorted(
            audit_df["Status"]
            .dropna()
            .astype(str)
            .unique()
            .tolist()
        )

        f1, f2 = st.columns(2)

        with f1:
            selected_events = st.multiselect(
                "Event Type",
                event_options,
                default=[],
                key="audit_event_filter",
            )

        with f2:
            selected_audit_status = st.multiselect(
                "Status",
                status_options,
                default=[],
                key="audit_status_filter",
            )

        filtered_audit = audit_df.copy()

        if selected_events:

            filtered_audit = (
                filtered_audit[
                    filtered_audit["Event"]
                    .astype(str)
                    .isin(
                        selected_events
                    )
                ]
            )

        if selected_audit_status:

            filtered_audit = (
                filtered_audit[
                    filtered_audit["Status"]
                    .astype(str)
                    .isin(
                        selected_audit_status
                    )
                ]
            )

        st.dataframe(
            filtered_audit,
            use_container_width=True,
            height=600,
            hide_index=True,
        )

        st.download_button(
            "📥 Download Audit Trail",
            data=filtered_audit.to_csv(
                index=False
            ),
            file_name="merchantops_audit.csv",
            mime="text/csv",
            key="download_audit",
        )

    else:

        st.info(
            "No audit events available."
        )


# ============================================================
# ARCHITECTURE
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">'
    "🔄 MerchantOps AI Architecture"
    "</div>",
    unsafe_allow_html=True,
)

st.code(
    """
MERCHANT
    ↓
MerchantOps Dashboard
    ↓
Product / Customer / Quantity / Price
    ↓
MerchantOps FastAPI
    ↓
Server-side Razorpay Order Creation
    ↓
PostgreSQL
    ↓
Customer Checkout
    ↓
Razorpay Test Mode
    ↓
┌─────────────────────────────┐
│ Checkout Signature Verify   │
│             +               │
│ Razorpay Webhook            │
└──────────────┬──────────────┘
               ↓
        MerchantOps AI
               ↓
    Revenue → Risk → Simulation
               ↓
        Decision Agent
               ↓
      Governance Guardrails
               ↓
      Merchant Dashboard
""",
    language="text",
)

st.divider()

st.caption(
    "MerchantOps AI • Payment Intelligence • "
    "Revenue Recovery • Risk Analysis • "
    "Agentic Decision Automation • Razorpay Test Mode"
)
