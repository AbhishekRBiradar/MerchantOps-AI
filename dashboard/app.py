from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = "http://127.0.0.1:8000"
AUDIT_FILE = Path("data/audit_log.jsonl")


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
        }

        .decision-card {
            border: 1px solid rgba(128,128,128,0.25);
            border-radius: 12px;
            padding: 16px;
            margin-bottom: 10px;
        }

        .risk-high {
            font-weight: 700;
        }

        .risk-medium {
            font-weight: 700;
        }

        .risk-low {
            font-weight: 700;
        }

        div[data-testid="stMetric"] {
            padding: 8px;
        }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# API HELPERS
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
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💳 MerchantOps AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    'Autonomous merchant intelligence, revenue recovery '
    'and governed AI decision automation'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Controls")

    if st.button(
        "🔄 Refresh Data",
        use_container_width=True,
    ):
        st.cache_data.clear()
        st.rerun()

    st.divider()

    st.caption(
        "Backend"
    )

    st.code(
        API_URL,
        language="text",
    )

    st.caption(
        "Mode: Test / Development"
    )


# ============================================================
# LOAD DATA
# ============================================================

try:

    payments_data = fetch_api(
        "/payments"
    )

    analysis_data = fetch_api(
        "/analyze"
    )

    decisions_data = fetch_api(
        "/decisions"
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


# ============================================================
# KPI OVERVIEW
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📊 Merchant Operations Overview'
    '</div>',
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
# EXECUTIVE SUMMARY
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🎯 AI Executive Summary'
    '</div>',
    unsafe_allow_html=True,
)

operations = analysis_data.get(
    "operations",
    {},
)

recovery_candidates = analysis_data.get(
    "recovery_candidates",
    0,
)

final_decisions = analysis_data.get(
    "decisions",
    0,
)

expected_recoveries = sum(
    float(
        decision.get(
            "expected_recovery",
            0,
        )
    )
    for decision in decisions_data.get(
        "decisions",
        [],
    )
)


s1, s2, s3, s4 = st.columns(4)

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
        f"₹{expected_recoveries:,.0f}",
    )

with s4:

    st.metric(
        "AI Decisions",
        f"{final_decisions:,}",
    )


# ============================================================
# ACTION BREAKDOWN
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🤖 AI Action Recommendations'
    '</div>',
    unsafe_allow_html=True,
)

action_counts = decisions_data.get(
    "action_counts",
    {},
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
            action_counts.get(
                "RETRY_NOW",
                0,
            ),
            action_counts.get(
                "RETRY_LATER",
                0,
            ),
            action_counts.get(
                "REVIEW",
                0,
            ),
            action_counts.get(
                "DO_NOTHING",
                0,
            ),
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
        action_counts.get(
            "RETRY_NOW",
            0,
        ),
    )

    st.metric(
        "Retry Later",
        action_counts.get(
            "RETRY_LATER",
            0,
        ),
    )

    st.metric(
        "Review",
        action_counts.get(
            "REVIEW",
            0,
        ),
    )

    st.metric(
        "Do Nothing",
        action_counts.get(
            "DO_NOTHING",
            0,
        ),
    )


st.divider()


# ============================================================
# GOVERNANCE
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🛡️ AI Governance & Safety'
    '</div>',
    unsafe_allow_html=True,
)

execution_modes = decisions_data.get(
    "execution_modes",
    {},
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
        execution_modes.get(
            "SCHEDULED_TEST_ACTION",
            0,
        ),
    )


# ============================================================
# DECISION DATA
# ============================================================

decisions = decisions_data.get(
    "decisions",
    [],
)


if decisions:

    decision_rows = []

    for decision in decisions:

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

else:

    decisions_df = pd.DataFrame()


# ============================================================
# FILTERS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🔎 Decision Explorer'
    '</div>',
    unsafe_allow_html=True,
)

f1, f2, f3 = st.columns(3)

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
        max_value=103,
        value=25,
        step=5,
    )


filtered_df = decisions_df.copy()

if selected_action != "ALL":

    filtered_df = filtered_df[
        filtered_df[
            "Decision"
        ] == selected_action
    ]

if selected_risk != "ALL":

    filtered_df = filtered_df[
        filtered_df[
            "Risk"
        ] == selected_risk
    ]


st.dataframe(
    filtered_df.head(max_rows),
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# APPROVAL QUEUE
# ============================================================

st.markdown(
    '<div class="section-title">'
    '⚠️ Merchant Approval Queue'
    '</div>',
    unsafe_allow_html=True,
)

approval_df = filtered_df[
    filtered_df[
        "Approval"
    ] == "YES"
].copy()


if approval_df.empty:

    st.info(
        "No approval actions currently require merchant review."
    )

else:

    st.warning(
        f"{len(approval_df)} decision(s) require merchant approval."
    )

    st.dataframe(
        approval_df,
        use_container_width=True,
        hide_index=True,
    )


# ============================================================
# DECISION DETAILS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🧠 Decision Details & Explainability'
    '</div>',
    unsafe_allow_html=True,
)

all_decisions = decisions_data.get(
    "decisions",
    [],
)

if all_decisions:

    payment_options = [
        str(
            decision.get(
                "payment_id"
            )
        )
        for decision in all_decisions
    ]

    selected_payment = st.selectbox(
        "Select a payment",
        payment_options,
    )

    selected = next(
        decision
        for decision in all_decisions
        if str(
            decision.get(
                "payment_id"
            )
        )
        == selected_payment
    )

    policy = selected.get(
        "policy",
        {},
    )

    d1, d2, d3, d4 = st.columns(4)

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
        f"**Failure reason:** {selected.get('failure_reason')}"
    )

    st.write(
        f"**Final decision:** {selected.get('final_action')}"
    )

    st.write(
        f"**Decision reason:** {selected.get('decision_reason')}"
    )

    st.write(
        f"**Policy mode:** {policy.get('execution_mode')}"
    )


# ============================================================
# SIMULATION DETAILS
# ============================================================

st.markdown(
    '<div class="section-title">'
    '🧪 Simulation Analysis'
    '</div>',
    unsafe_allow_html=True,
)

if all_decisions:

    selected_sim = st.selectbox(
        "Select payment for simulation",
        payment_options,
        key="simulation_payment",
    )

    simulation_decision = next(
        decision
        for decision in all_decisions
        if str(
            decision.get(
                "payment_id"
            )
        )
        == selected_sim
    )

    scenarios = simulation_decision.get(
        "simulation_scenarios",
        [],
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

        st.bar_chart(
            simulation_df.set_index(
                "action"
            )["expected_recovery"]
        )


# ============================================================
# AUDIT TRAIL
# ============================================================

st.markdown(
    '<div class="section-title">'
    '📋 Audit Trail'
    '</div>',
    unsafe_allow_html=True,
)

audit_events = load_audit_events()

if audit_events:

    audit_rows = []

    for event in audit_events[-50:]:

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
        audit_df.sort_values(
            by="Timestamp",
            ascending=False,
        ),
        use_container_width=True,
        hide_index=True,
    )

else:

    st.info(
        "No audit events available yet."
    )


# ============================================================
# PIPELINE
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">'
    '🔄 MerchantOps AI Pipeline'
    '</div>',
    unsafe_allow_html=True,
)

st.code(
    """
Payment Data
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
Merchant
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
    "Agentic Decision Automation • Test Environment"
)