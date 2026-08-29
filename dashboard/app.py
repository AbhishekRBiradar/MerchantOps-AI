from __future__ import annotations

import os
from typing import Any, Dict, Optional

import pandas as pd
import requests
import streamlit as st

from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()

API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000",
).rstrip("/")


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MerchantOps AI",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# CUSTOM STYLING
# ============================================================

st.markdown(
    """
    <style>

    .main-title {
        font-size: 42px;
        font-weight: 750;
        margin-bottom: 4px;
    }

    .subtitle {
        font-size: 17px;
        opacity: 0.72;
        margin-bottom: 18px;
    }

    .section-title {
        font-size: 28px;
        font-weight: 700;
        margin-top: 14px;
        margin-bottom: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API GET
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
# API POST
# ============================================================

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
        if payment_source_label
        == "Razorpay Test Mode"
        else "csv"
    )

    if st.button(
        "🔄 Refresh Data",
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
        f"Active source: {payment_source_label}"
    )

    st.caption(
        "Mode: Test / Development"
    )


# ============================================================
# LOAD BACKEND DATA
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

except Exception as exc:

    st.error(
        "❌ Unable to connect to MerchantOps API."
    )

    st.code(
        str(exc)
    )

    st.info(
        "Check that the FastAPI backend is running "
        "and API_URL is configured correctly."
    )

    st.stop()


# ============================================================
# EXTRACT DATA
# ============================================================

audit_events = (
    audit_data.get(
        "events",
        [],
    )
)

webhook_events = (
    webhook_data.get(
        "events",
        [],
    )
)

verified_payments = (
    verified_data.get(
        "payments",
        [],
    )
)

decision_records = (
    decisions_data.get(
        "decisions",
        [],
    )
)


# ============================================================
# API CONNECTION STATUS
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
    f"Active payment source: **{payment_source_label}**"
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

operations = analysis_data.get(
    "operations",
    {},
)


total_payments = int(
    payments_data.get(
        "total_payments",
        operations.get(
            "total_payments",
            0,
        ),
    )
)

failed_payments = int(
    payments_data.get(
        "failed_payments",
        operations.get(
            "failed_payments",
            0,
        ),
    )
)

captured_payments = int(
    payments_data.get(
        "captured_payments",
        operations.get(
            "captured_payments",
            0,
        ),
    )
)

failure_rate = float(
    payments_data.get(
        "failure_rate",
        operations.get(
            "failure_rate",
            0.0,
        ),
    )
)

revenue_at_risk = float(
    payments_data.get(
        "revenue_at_risk",
        operations.get(
            "revenue_at_risk",
            0.0,
        ),
    )
)


success_rate = (

    (
        captured_payments
        / total_payments
        * 100
    )

    if total_payments > 0

    else 0.0
)


c1, c2, c3, c4, c5 = st.columns(5)


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


# IMPORTANT:
# These values come directly from PostgreSQL through
# /activity/stats. We do NOT calculate them from the
# latest 1000 audit records.

verified_payment_count = int(
    activity_data.get(
        "verified_payments",
        0,
    )
)

verification_event_count = int(
    activity_data.get(
        "verification_events",
        0,
    )
)

webhook_event_count = int(
    activity_data.get(
        "webhook_events",
        0,
    )
)

webhook_processing_count = int(
    activity_data.get(
        "webhook_processing",
        0,
    )
)


r1, r2, r3, r4 = st.columns(4)


with r1:

    st.metric(
        "Verified Payments",
        verified_payment_count,
    )


with r2:

    st.metric(
        "Verification Events",
        verification_event_count,
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


# ============================================================
# RECENTLY VERIFIED PAYMENTS
# ============================================================

st.markdown(
    "#### Recently Verified Payments"
)


if verified_payments:

    verified_df = pd.DataFrame(
        verified_payments
    )

    st.dataframe(
        verified_df.head(10),
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No verified Razorpay payments found."
    )


st.divider()


# ============================================================
# RAZORPAY WEBHOOK ACTIVITY
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
        webhook_df.head(20),
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No Razorpay webhook events found."
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


recovery_candidates = int(
    analysis_data.get(
        "recovery_candidates",
        0,
    )
)


ai_decision_count = int(
    analysis_data.get(
        "decisions",
        decisions_data.get(
            "count",
            0,
        ),
    )
)


expected_recovery = sum(
    float(
        decision.get(
            "expected_recovery",
            0,
        )
        or 0
    )

    for decision
    in decision_records
)


s1, s2, s3, s4 = st.columns(4)


with s1:

    st.metric(
        "Revenue at Risk",
        f"₹{revenue_at_risk:,.0f}",
    )


with s2:

    st.metric(
        "Recovery Candidates",
        recovery_candidates,
    )


with s3:

    st.metric(
        "Expected Recovery",
        f"₹{expected_recovery:,.0f}",
    )


with s4:

    st.metric(
        "AI Decisions",
        ai_decision_count,
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


action_counts = (
    decisions_data.get(
        "action_counts",
        {},
    )
)


retry_now_count = int(
    action_counts.get(
        "RETRY_NOW",
        0,
    )
)

retry_later_count = int(
    action_counts.get(
        "RETRY_LATER",
        0,
    )
)

review_count = int(
    action_counts.get(
        "REVIEW",
        0,
    )
)

do_nothing_count = int(
    action_counts.get(
        "DO_NOTHING",
        0,
    )
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
            retry_now_count,
            retry_later_count,
            review_count,
            do_nothing_count,
        ],
    }
)


ac1, ac2 = st.columns(
    [2, 1]
)


with ac1:

    st.bar_chart(
        action_df.set_index(
            "Action"
        )
    )


with ac2:

    st.metric(
        "RETRY_NOW",
        retry_now_count,
    )

    st.metric(
        "RETRY_LATER",
        retry_later_count,
    )

    st.metric(
        "REVIEW",
        review_count,
    )

    st.metric(
        "DO_NOTHING",
        do_nothing_count,
    )


st.divider()


# ============================================================
# GOVERNANCE & SAFETY
# ============================================================

st.markdown(
    '<div class="section-title">'
    "🛡️ AI Governance & Safety"
    "</div>",
    unsafe_allow_html=True,
)


execution_modes = (
    decisions_data.get(
        "execution_modes",
        {},
    )
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


g1, g2, g3, g4 = st.columns(4)


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
            {},
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
                        or 0
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
                        or 0
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
            }
        )


    decision_df = pd.DataFrame(
        decision_rows
    )


    col_a, col_b, col_c = st.columns(3)


    with col_a:

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


    with col_b:

        selected_risk = st.selectbox(
            "Risk",
            [
                "ALL",
                "LOW",
                "MEDIUM",
                "HIGH",
            ],
        )


    with col_c:

        row_limit = st.number_input(
            "Rows",
            min_value=1,
            max_value=1000,
            value=10,
            step=1,
        )


    filtered_df = (
        decision_df.copy()
    )


    if selected_action != "ALL":

        filtered_df = filtered_df[
            filtered_df["Decision"]
            ==
            selected_action
        ]


    if selected_risk != "ALL":

        filtered_df = filtered_df[
            filtered_df["Risk"]
            ==
            selected_risk
        ]


    st.dataframe(
        filtered_df.head(
            int(row_limit)
        ),
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No AI decisions available."
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
        f"{len(approval_df)} decision(s) "
        "require merchant approval."
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


st.divider()


# ============================================================
# DECISION DETAILS & EXPLAINABILITY
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

        for decision
        in decision_records
    ]


    selected_payment = st.selectbox(
        "Select a payment",
        payment_options,
        key="decision_payment",
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

        decision_records[0],
    )


    selected_policy = (
        selected_decision.get(
            "policy",
            {},
        )
    )


    d1, d2, d3, d4 = st.columns(4)


    with d1:

        st.metric(
            "Amount",
            (
                "₹"
                f"{float(selected_decision.get('amount', 0) or 0):,.0f}"
            ),
        )


    with d2:

        st.metric(
            "Risk Score",
            (
                f"{float(selected_decision.get('risk_score', 0) or 0):.2f}"
            ),
        )


    with d3:

        st.metric(
            "Expected Recovery",
            (
                "₹"
                f"{float(selected_decision.get('expected_recovery', 0) or 0):,.0f}"
            ),
        )


    with d4:

        confidence = float(
            selected_decision.get(
                "decision_confidence",
                0,
            )
            or 0
        )

        st.metric(
            "Confidence",
            f"{confidence * 100:.1f}%",
        )


    st.write(
        "**Payment:** "
        f"{selected_decision.get('payment_id')}"
    )

    st.write(
        "**Order:** "
        f"{selected_decision.get('order_id')}"
    )

    st.write(
        "**Customer:** "
        f"{selected_decision.get('customer_id')}"
    )

    st.write(
        "**Payment Method:** "
        f"{selected_decision.get('payment_method')}"
    )

    st.write(
        "**Failure Reason:** "
        f"{selected_decision.get('failure_reason')}"
    )

    st.write(
        "**Final Decision:** "
        f"{selected_decision.get('final_action')}"
    )

    st.write(
        "**Decision Reason:** "
        f"{selected_decision.get('decision_reason')}"
    )

    st.write(
        "**Policy Mode:** "
        f"{selected_policy.get('execution_mode')}"
    )


else:

    st.info(
        "No decision details available."
    )


st.divider()


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

    simulation_payment = st.selectbox(
        "Select payment for simulation",
        payment_options,
        key="simulation_payment",
    )


    simulation_decision = next(
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
            simulation_payment
        ),

        decision_records[0],
    )


    scenarios = (
        simulation_decision.get(
            "simulation_scenarios",
            [],
        )
    )


    if scenarios:

        simulation_df = pd.DataFrame(
            scenarios
        )

        st.dataframe(
            simulation_df,
            use_container_width=True,
            hide_index=True,
        )


        if {
            "action",
            "expected_recovery",
        }.issubset(
            simulation_df.columns
        ):

            chart_df = (
                simulation_df[
                    [
                        "action",
                        "expected_recovery",
                    ]
                ]
                .set_index(
                    "action"
                )
            )

            st.bar_chart(
                chart_df
            )

    else:

        st.info(
            "No simulation scenarios available."
        )

else:

    st.info(
        "No simulation data available."
    )


st.divider()


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

    verified_detail_df = pd.DataFrame(
        verified_payments
    )

    st.dataframe(
        verified_detail_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No verified payment records available."
    )


st.divider()


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
        audit_df,
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No audit events available."
    )


st.divider()


# ============================================================
# ARCHITECTURE
# ============================================================

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
PostgreSQL
       ↓
MerchantOps API
       ↓
Streamlit Dashboard

Razorpay Webhook
       ↓
Signature Verification
       ↓
x-razorpay-event-id
       ↓
PostgreSQL Idempotency
       ↓
Webhook Processor
       ↓
MerchantOps AI
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