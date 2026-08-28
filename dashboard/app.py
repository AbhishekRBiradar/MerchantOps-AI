from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")

AUDIT_FILE = Path(
    "data/audit_log.jsonl"
)

DEFAULT_SOURCE = "csv"


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="MerchantOps AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

        .main-title {
            font-size: 44px;
            font-weight: 750;
            margin-bottom: 2px;
        }

        .subtitle {
            font-size: 17px;
            opacity: 0.72;
            margin-bottom: 20px;
        }

        .section-title {
            font-size: 28px;
            font-weight: 700;
            margin-top: 10px;
            margin-bottom: 12px;
        }

        div[data-testid="stMetric"] {
            padding: 8px;
        }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API HELPER
# ============================================================

@st.cache_data(ttl=10)
def fetch_api(
    endpoint: str,
) -> Dict[str, Any]:

    response = requests.get(
        f"{API_URL}{endpoint}",
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


# ============================================================
# AUDIT LOADER
# ============================================================

def load_audit_events() -> List[Dict[str, Any]]:

    if not AUDIT_FILE.exists():
        return []

    events: List[Dict[str, Any]] = []

    with AUDIT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:

        for line in file:

            line = line.strip()

            if not line:
                continue

            try:

                events.append(
                    json.loads(line)
                )

            except json.JSONDecodeError:

                continue

    return events


# ============================================================
# AUDIT HELPERS
# ============================================================

def get_event_count(
    events: List[Dict[str, Any]],
    event_type: str,
) -> int:

    return sum(
        1
        for event in events
        if event.get("event_type")
        == event_type
    )


def get_verified_payments(
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    verified = []

    for event in events:

        if (
            event.get("event_type")
            != "PAYMENT_VERIFICATION"
        ):
            continue

        if (
            event.get("status")
            != "VERIFIED"
        ):
            continue

        details = event.get(
            "details",
            {},
        )

        verified.append(
            {
                "Timestamp":
                    event.get(
                        "timestamp"
                    ),

                "Payment ID":
                    event.get(
                        "payment_id"
                    ),

                "Order ID":
                    details.get(
                        "order_id"
                    ),

                "Amount":
                    details.get(
                        "amount"
                    ),

                "Currency":
                    details.get(
                        "currency"
                    ),

                "Payment Status":
                    details.get(
                        "payment_status"
                    ),

                "Payment Method":
                    details.get(
                        "payment_method"
                    ),

                "Captured":
                    details.get(
                        "captured"
                    ),
            }
        )

    return verified


def get_webhook_events(
    events: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:

    webhook_events = []

    for event in events:

        if (
            event.get("event_type")
            != "RAZORPAY_WEBHOOK"
        ):
            continue

        details = event.get(
            "details",
            {},
        )

        webhook_events.append(
            {
                "Timestamp":
                    event.get(
                        "timestamp"
                    ),

                "Event":
                    event.get(
                        "action"
                    ),

                "Event ID":
                    details.get(
                        "event_id"
                    ),

                "Payment ID":
                    event.get(
                        "payment_id"
                    ),

                "Order ID":
                    details.get(
                        "order_id"
                    ),

                "Payment Status":
                    details.get(
                        "payment_status"
                    ),

                "Status":
                    event.get(
                        "status"
                    ),
            }
        )

    return webhook_events


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💳 MerchantOps AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Autonomous merchant intelligence, revenue recovery "
    "and governed AI decision automation"
    "</div>",
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

with st.sidebar:

    st.header("⚙️ Controls")

    # --------------------------------------------------------
    # PAYMENT DATA SOURCE
    # --------------------------------------------------------

    source_label = st.radio(
        "Payment Data Source",
        [
            "Demo Dataset",
            "Razorpay Test Mode",
        ],
        index=(
            0
            if DEFAULT_SOURCE == "csv"
            else 1
        ),
    )

    source = (
        "razorpay"
        if source_label
        == "Razorpay Test Mode"
        else "csv"
    )

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    if st.button(
        "🔄 Refresh Data",
        use_container_width=True,
    ):

        st.cache_data.clear()

        st.rerun()

    st.divider()

    # --------------------------------------------------------
    # BACKEND INFORMATION
    # --------------------------------------------------------

    st.caption(
        "Backend"
    )

    st.code(
        API_URL,
        language="text",
    )

    st.caption(
        f"Active source: {source_label}"
    )

    st.caption(
        "Mode: Test / Development"
    )


# ============================================================
# LOAD API DATA
# ============================================================

try:

    payments_data = fetch_api(
        f"/payments?source={source}"
    )

    analysis_data = fetch_api(
        f"/analyze?source={source}"
    )

    decisions_data = fetch_api(
        f"/decisions?source={source}"
    )

except Exception as exc:

    st.error(
        "Unable to connect to the MerchantOps API."
    )

    st.code(
        str(exc)
    )

    st.info(
        "Start FastAPI with:\n\n"
        "python -m uvicorn backend.main:app --reload"
    )

    st.stop()


# ============================================================
# LOAD AUDIT DATA
# ============================================================

audit_events = load_audit_events()

verified_payments = (
    get_verified_payments(
        audit_events
    )
)

webhook_events = (
    get_webhook_events(
        audit_events
    )
)

payment_verification_count = (
    get_event_count(
        audit_events,
        "PAYMENT_VERIFICATION",
    )
)

webhook_event_count = (
    get_event_count(
        audit_events,
        "RAZORPAY_WEBHOOK",
    )
)

webhook_processing_count = (
    get_event_count(
        audit_events,
        "WEBHOOK_PROCESSING",
    )
)


# ============================================================
# API STATUS
# ============================================================

status_col1, status_col2 = st.columns(
    [5, 1]
)

with status_col1:

    st.success(
        "🟢 MerchantOps API Connected"
    )

with status_col2:

    st.caption(
        "Live API"
    )


st.info(
    f"Active payment source: **{source_label}**"
)


# ============================================================
# OPERATIONS OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">'
    "📊 Merchant Operations Overview"
    "</div>",
    unsafe_allow_html=True,
)

total_payments = int(
    payments_data.get(
        "total_payments",
        0,
    )
)

failed_payments = int(
    payments_data.get(
        "failed_payments",
        0,
    )
)

captured_payments = int(
    payments_data.get(
        "captured_payments",
        0,
    )
)

failure_rate = float(
    payments_data.get(
        "failure_rate",
        0,
    )
)

revenue_at_risk = float(
    payments_data.get(
        "revenue_at_risk",
        0,
    )
)

success_rate = (
    captured_payments
    / total_payments
    * 100
    if total_payments > 0
    else 0.0
)


c1, c2, c3, c4, c5 = st.columns(
    5
)

with c1:

    st.metric(
        "Total Payments",
        f"{total_payments:,}",
    )

with c2:

    st.metric(
        "Failed Payments",
        f"{failed_payments:,}",
    )

with c3:

    st.metric(
        "Success Rate",
        f"{success_rate:.1f}%",
    )

with c4:

    st.metric(
        "Failure Rate",
        f"{failure_rate:.1f}%",
    )

with c5:

    st.metric(
        "Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}",
    )


st.divider()


# ============================================================
# RAZORPAY LIVE ACTIVITY
# ============================================================

st.markdown(
    '<div class="section-title">'
    "💳 Razorpay Live Activity"
    "</div>",
    unsafe_allow_html=True,
)

r1, r2, r3, r4 = st.columns(
    4
)

with r1:

    st.metric(
        "Verified Payments",
        len(verified_payments),
    )

with r2:

    st.metric(
        "Verification Events",
        payment_verification_count,
    )

with r3:

    st.metric(
        "Webhook Events",
        webhook_event_count,
    )

with r4:

    st.metric(
        "Webhook Processing",
        webhook_processing_count,
    )


if source == "razorpay":

    if verified_payments:

        verified_df = pd.DataFrame(
            verified_payments
        )

        st.markdown(
            "#### Recently Verified Payments"
        )

        st.dataframe(
            verified_df.tail(10).iloc[::-1],
            use_container_width=True,
            hide_index=True,
        )

    else:

        st.info(
            "No verified Razorpay payments recorded yet."
        )


st.divider()


# ============================================================
# WEBHOOK ACTIVITY
# ============================================================

st.markdown(
    '<div class="section-title">'
    "🔔 Razorpay Webhook Activity"
    "</div>",
    unsafe_allow_html=True,
)

if webhook_events:

    webhook_df = pd.DataFrame(
        webhook_events
    )

    st.dataframe(
        webhook_df.tail(20).iloc[::-1],
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No Razorpay webhook events recorded yet."
    )


st.divider()


# ============================================================
# AI EXECUTIVE SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">'
    "🤖 AI Executive Summary"
    "</div>",
    unsafe_allow_html=True,
)

operations = analysis_data.get(
    "operations",
    {},
)

recovery_candidates = int(
    analysis_data.get(
        "recovery_candidates",
        0,
    )
)

final_decisions = int(
    analysis_data.get(
        "decisions",
        0,
    )
)

decision_records = decisions_data.get(
    "decisions",
    []
)

expected_recovery = sum(
    float(
        decision.get(
            "expected_recovery",
            0,
        )
    )
    for decision in decision_records
)


s1, s2, s3, s4 = st.columns(
    4
)

with s1:

    st.metric(
        "Revenue at Risk",
        f"₹{float(operations.get('revenue_at_risk', 0)):,.0f}",
    )

with s2:

    st.metric(
        "Recovery Candidates",
        f"{recovery_candidates:,}",
    )

with s3:

    st.metric(
        "Expected Recovery",
        f"₹{expected_recovery:,.0f}",
    )

with s4:

    st.metric(
        "AI Decisions",
        f"{final_decisions:,}",
    )


st.divider()


# ============================================================
# AI ACTION RECOMMENDATIONS
# ============================================================

st.markdown(
    '<div class="section-title">'
    "🎯 AI Action Recommendations"
    "</div>",
    unsafe_allow_html=True,
)

action_counts = decisions_data.get(
    "action_counts",
    {}
)

retry_now = int(
    action_counts.get(
        "RETRY_NOW",
        0,
    )
)

retry_later = int(
    action_counts.get(
        "RETRY_LATER",
        0,
    )
)

review = int(
    action_counts.get(
        "REVIEW",
        0,
    )
)

do_nothing = int(
    action_counts.get(
        "DO_NOTHING",
        0,
    )
)


actions_df = pd.DataFrame(
    {
        "Action": [
            "RETRY_NOW",
            "RETRY_LATER",
            "REVIEW",
            "DO_NOTHING",
        ],
        "Count": [
            retry_now,
            retry_later,
            review,
            do_nothing,
        ],
    }
)


chart_col, metric_col = st.columns(
    [2, 1]
)

with chart_col:

    st.bar_chart(
        actions_df.set_index(
            "Action"
        )
    )

with metric_col:

    st.metric(
        "Retry Now",
        retry_now,
    )

    st.metric(
        "Retry Later",
        retry_later,
    )

    st.metric(
        "Review",
        review,
    )

    st.metric(
        "Do Nothing",
        do_nothing,
    )


st.divider()


# ============================================================
# AI GOVERNANCE
# ============================================================

st.markdown(
    '<div class="section-title">'
    "🛡️ AI Governance & Safety"
    "</div>",
    unsafe_allow_html=True,
)

execution_modes = decisions_data.get(
    "execution_modes",
    {}
)

approval_required = int(
    decisions_data.get(
        "approval_required",
        0,
    )
)

allowed_actions = int(
    decisions_data.get(
        "allowed_actions",
        0,
    )
)

blocked_actions = int(
    decisions_data.get(
        "blocked_actions",
        0,
    )
)

scheduled_actions = int(
    execution_modes.get(
        "SCHEDULED_TEST_ACTION",
        0,
    )
)


g1, g2, g3, g4 = st.columns(
    4
)

with g1:

    st.metric(
        "Merchant Approval",
        approval_required,
    )

with g2:

    st.metric(
        "Allowed Actions",
        allowed_actions,
    )

with g3:

    st.metric(
        "Blocked Actions",
        blocked_actions,
    )

with g4:

    st.metric(
        "Scheduled Test Actions",
        scheduled_actions,
    )


st.divider()


# ============================================================
# DECISION EXPLORER
# ============================================================

st.markdown(
    '<div class="section-title">'
    "🔎 Decision Explorer"
    "</div>",
    unsafe_allow_html=True,
)

if decision_records:

    decision_rows = []

    for decision in decision_records:

        policy = decision.get(
            "policy",
            {}
        )

        decision_rows.append(
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
                    float(
                        decision.get(
                            "amount",
                            0,
                        )
                    ),

                "Risk":
                    decision.get(
                        "risk_level"
                    ),

                "Risk Score":
                    decision.get(
                        "risk_score"
                    ),

                "Expected Recovery":
                    float(
                        decision.get(
                            "expected_recovery",
                            0,
                        )
                    ),

                "Decision":
                    decision.get(
                        "final_action"
                    ),

                "Approval":
                    (
                        "YES"
                        if decision.get(
                            "approval_required"
                        )
                        else "NO"
                    ),

                "Execution Mode":
                    policy.get(
                        "execution_mode"
                    ),

                "Reason":
                    decision.get(
                        "decision_reason"
                    ),
            }
        )

    decisions_df = pd.DataFrame(
        decision_rows
    )

    f1, f2, f3 = st.columns(
        3
    )

    with f1:

        selected_action = st.selectbox(
            "Action",
            [
                "ALL",
                "RETRY_NOW",
                "RETRY_LATER",
                "REVIEW",
                "DO_NOTHING",
            ],
        )

    with f2:

        selected_risk = st.selectbox(
            "Risk",
            [
                "ALL",
                "LOW",
                "MEDIUM",
                "HIGH",
            ],
        )

    with f3:

        max_rows = st.slider(
            "Rows",
            min_value=10,
            max_value=max(
                10,
                len(decisions_df),
            ),
            value=min(
                25,
                len(decisions_df),
            ),
            step=5,
        )

    filtered_df = decisions_df.copy()

    if selected_action != "ALL":

        filtered_df = filtered_df[
            filtered_df["Decision"]
            == selected_action
        ]

    if selected_risk != "ALL":

        filtered_df = filtered_df[
            filtered_df["Risk"]
            == selected_risk
        ]

    st.dataframe(
        filtered_df.head(
            max_rows
        ),
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No AI decisions available for this payment source."
    )


st.divider()


# ============================================================
# MERCHANT APPROVAL QUEUE
# ============================================================

st.markdown(
    '<div class="section-title">'
    "⏳ Merchant Approval Queue"
    "</div>",
    unsafe_allow_html=True,
)

approval_rows = []

for decision in decision_records:

    if decision.get(
        "approval_required",
        False,
    ):

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
                    decision.get(
                        "amount"
                    ),

                "Risk":
                    decision.get(
                        "risk_level"
                    ),

                "Risk Score":
                    decision.get(
                        "risk_score"
                    ),

                "Expected Recovery":
                    decision.get(
                        "expected_recovery"
                    ),

                "Recommended Action":
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

    approval_df = pd.DataFrame(
        approval_rows
    )

    st.warning(
        f"{len(approval_df)} decision(s) require merchant approval."
    )

    st.dataframe(
        approval_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No merchant approvals currently required."
    )


# ============================================================
# DECISION DETAILS
# ============================================================

st.markdown(
    '<div class="section-title">'
    "🧠 Decision Details & Explainability"
    "</div>",
    unsafe_allow_html=True,
)

if decision_records:

    payment_options = [
        str(
            decision.get(
                "payment_id"
            )
        )
        for decision in decision_records
    ]

    selected_payment = st.selectbox(
        "Select a payment",
        payment_options,
        key="decision_payment",
    )

    selected = next(
        decision
        for decision in decision_records
        if str(
            decision.get(
                "payment_id"
            )
        )
        == selected_payment
    )

    policy = selected.get(
        "policy",
        {}
    )

    d1, d2, d3, d4 = st.columns(
        4
    )

    with d1:

        st.metric(
            "Amount",
            f"₹{float(selected.get('amount', 0)):,.0f}",
        )

    with d2:

        st.metric(
            "Risk Score",
            f"{float(selected.get('risk_score', 0)):.2f}",
        )

    with d3:

        st.metric(
            "Expected Recovery",
            f"₹{float(selected.get('expected_recovery', 0)):,.0f}",
        )

    with d4:

        st.metric(
            "Confidence",
            f"{float(selected.get('decision_confidence', 0)) * 100:.1f}%",
        )

    st.write(
        f"**Payment:** {selected.get('payment_id')}"
    )

    st.write(
        f"**Order:** {selected.get('order_id')}"
    )

    st.write(
        f"**Customer:** {selected.get('customer_id')}"
    )

    st.write(
        f"**Payment Method:** {selected.get('payment_method')}"
    )

    st.write(
        f"**Failure Reason:** {selected.get('failure_reason')}"
    )

    st.write(
        f"**Final Decision:** {selected.get('final_action')}"
    )

    st.write(
        f"**Decision Reason:** {selected.get('decision_reason')}"
    )

    st.write(
        f"**Policy Mode:** {policy.get('execution_mode')}"
    )


# ============================================================
# SIMULATION ANALYSIS
# ============================================================

st.markdown(
    '<div class="section-title">'
    "🧪 Simulation Analysis"
    "</div>",
    unsafe_allow_html=True,
)

if decision_records:

    selected_simulation = st.selectbox(
        "Select payment for simulation",
        payment_options,
        key="simulation_payment",
    )

    simulation_decision = next(
        decision
        for decision in decision_records
        if str(
            decision.get(
                "payment_id"
            )
        )
        == selected_simulation
    )

    scenarios = simulation_decision.get(
        "simulation_scenarios",
        []
    )

    simulation_df = pd.DataFrame(
        scenarios
    )

    if not simulation_df.empty:

        st.dataframe(
            simulation_df,
            use_container_width=True,
            hide_index=True,
        )

        if "expected_recovery" in simulation_df.columns:

            st.bar_chart(
                simulation_df.set_index(
                    "action"
                )[
                    "expected_recovery"
                ]
            )

else:

    st.info(
        "No simulation data available."
    )


# ============================================================
# VERIFIED PAYMENT DETAILS
# ============================================================

st.markdown(
    '<div class="section-title">'
    "✅ Verified Payment Details"
    "</div>",
    unsafe_allow_html=True,
)

if verified_payments:

    verification_df = pd.DataFrame(
        verified_payments
    )

    st.dataframe(
        verification_df.tail(20).iloc[::-1],
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No verified payment records found in the audit log."
    )


# ============================================================
# AUDIT TRAIL
# ============================================================

st.markdown(
    '<div class="section-title">'
    "📋 Audit Trail"
    "</div>",
    unsafe_allow_html=True,
)

if audit_events:

    audit_rows = []

    for event in audit_events[-100:]:

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

                "Mode":
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

    st.dataframe(
        audit_df.iloc[::-1],
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No audit events available yet."
    )


# ============================================================
# SYSTEM ARCHITECTURE
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
Razorpay Checkout
       ↓
Create Order
       ↓
Payment
       ↓
Backend Signature Verification
       ↓
Payment Provider / Adapter
       ↓
Revenue Agent
       ↓
Risk Agent
       ↓
Simulation Agent
       ↓
Decision Agent
       ↓
Action Guardrails
       ↓
Audit Logging
       ↓
MerchantOps Dashboard

Razorpay Webhook
       ↓
Signature Verification
       ↓
Idempotency Check
       ↓
Webhook Processor
       ↓
MerchantOps AI Pipeline
       ↓
Audit
""",
    language="text",
)


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "MerchantOps AI • Payment Intelligence • "
    "Revenue Recovery • Risk Analysis • "
    "Agentic Decision Automation • "
    "Razorpay Test Mode"
)