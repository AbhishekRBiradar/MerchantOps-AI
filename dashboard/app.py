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

CHECKOUT_URL = os.getenv(
    "CHECKOUT_URL",
    "http://127.0.0.1:5500/razorpay/checkout.html",
)


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
# STYLING
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

    .order-card {
        padding: 18px;
        border-radius: 14px;
        border: 1px solid rgba(128,128,128,0.25);
        margin-top: 12px;
        margin-bottom: 12px;
    }

    .muted {
        opacity: 0.7;
        font-size: 13px;
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
# API ERROR HELPER
# ============================================================

def api_error_text(
    exc: Exception,
) -> str:

    return str(exc)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">💳 MerchantOps AI</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="subtitle">'
    "Merchant operations console for payment intelligence, "
    "revenue recovery, governed AI decisions and Razorpay "
    "payment operations."
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
        "Analytics Payment Data Source",
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
        f"Analytics source: {payment_source_label}"
    )

    st.caption(
        "Merchant payment operations use Razorpay Test Mode."
    )

    st.divider()

    st.caption("Customer Checkout")

    st.code(
        CHECKOUT_URL,
        language="text",
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

    merchant_orders_data = fetch_api(
        "/merchant/orders"
    )

except Exception as exc:

    st.error(
        "❌ Unable to connect to MerchantOps API."
    )

    st.code(
        api_error_text(exc)
    )

    st.info(
        "Check that FastAPI is running and API_URL "
        "is configured correctly."
    )

    st.stop()


# ============================================================
# EXTRACT
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

merchant_orders = (
    merchant_orders_data.get(
        "orders",
        [],
    )
)


# ============================================================
# CONNECTION STATUS
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
# NAVIGATION
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

    st.info(
        f"Analytics source: **{payment_source_label}**"
    )

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


    # --------------------------------------------------------
    # MERCHANT ORDERS
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        "🛒 Merchant Order Activity"
        "</div>",
        unsafe_allow_html=True,
    )

    created_count = sum(
        str(
            order.get(
                "status",
                "",
            )
        ).upper()
        == "CREATED"
        for order in merchant_orders
    )

    authorized_count = sum(
        str(
            order.get(
                "status",
                "",
            )
        ).upper()
        == "AUTHORIZED"
        for order in merchant_orders
    )

    captured_count = sum(
        str(
            order.get(
                "status",
                "",
            )
        ).upper()
        == "CAPTURED"
        for order in merchant_orders
    )

    verified_count = sum(
        str(
            order.get(
                "status",
                "",
            )
        ).upper()
        == "VERIFIED"
        for order in merchant_orders
    )

    failed_count = sum(
        str(
            order.get(
                "status",
                "",
            )
        ).upper()
        == "FAILED"
        for order in merchant_orders
    )

    m1, m2, m3, m4, m5 = st.columns(5)

    with m1:
        st.metric(
            "Merchant Orders",
            len(
                merchant_orders
            ),
        )

    with m2:
        st.metric(
            "Created",
            created_count,
        )

    with m3:
        st.metric(
            "Authorized",
            authorized_count,
        )

    with m4:
        st.metric(
            "Captured / Verified",
            captured_count
            + verified_count,
        )

    with m5:
        st.metric(
            "Failed",
            failed_count,
        )

    st.divider()


    # --------------------------------------------------------
    # RAZORPAY ACTIVITY
    # --------------------------------------------------------

    st.markdown(
        '<div class="section-title">'
        "💳 Razorpay Live Activity"
        "</div>",
        unsafe_allow_html=True,
    )

    r1, r2, r3, r4 = st.columns(4)

    with r1:
        st.metric(
            "Verified Payments",
            int(
                activity_data.get(
                    "verified_payments",
                    0,
                )
            ),
        )

    with r2:
        st.metric(
            "Verification Events",
            int(
                activity_data.get(
                    "verification_events",
                    0,
                )
            ),
        )

    with r3:
        st.metric(
            "Webhook Events",
            int(
                activity_data.get(
                    "webhook_events",
                    0,
                )
            ),
        )

    with r4:
        st.metric(
            "Webhook Processing",
            int(
                activity_data.get(
                    "webhook_processing",
                    0,
                )
            ),
        )

    st.divider()


    # --------------------------------------------------------
    # AI SUMMARY
    # --------------------------------------------------------

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
        for decision in decision_records
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


    # --------------------------------------------------------
    # ACTION COUNTS
    # --------------------------------------------------------

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

    action_df = pd.DataFrame(
        {
            "Action": [
                "RETRY_NOW",
                "RETRY_LATER",
                "REVIEW",
                "DO_NOTHING",
            ],
            "Count": [
                int(
                    action_counts.get(
                        "RETRY_NOW",
                        0,
                    )
                ),
                int(
                    action_counts.get(
                        "RETRY_LATER",
                        0,
                    )
                ),
                int(
                    action_counts.get(
                        "REVIEW",
                        0,
                    )
                ),
                int(
                    action_counts.get(
                        "DO_NOTHING",
                        0,
                    )
                ),
            ],
        }
    )

    a1, a2 = st.columns(
        [2, 1]
    )

    with a1:

        st.bar_chart(
            action_df.set_index(
                "Action"
            )
        )

    with a2:

        for _, row in action_df.iterrows():

            st.metric(
                str(
                    row["Action"]
                ),
                int(
                    row["Count"]
                ),
            )


    st.divider()


    # --------------------------------------------------------
    # GOVERNANCE
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # RECENT VERIFIED PAYMENTS
    # --------------------------------------------------------

    st.markdown(
        "### Recently Verified Payments"
    )

    if verified_payments:

        verified_df = pd.DataFrame(
            verified_payments
        )

        st.dataframe(
            verified_df.head(10),
            use_container_width=True,
            height=350,
            hide_index=True,
        )

    else:

        st.info(
            "No verified Razorpay payments found."
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
        "price, discount and tax. The backend creates "
        "the authoritative Razorpay order amount."
    )

    with st.form(
        "merchant_order_form",
        clear_on_submit=False,
    ):

        st.markdown(
            "### 👤 Customer"
        )

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


        st.markdown(
            "### 🛍️ Product"
        )

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
                max_value=10_000_000.00,
                value=1499.00,
                step=1.00,
            )

        with p3:

            discount = st.number_input(
                "Discount (₹)",
                min_value=0.00,
                max_value=10_000_000.00,
                value=0.00,
                step=1.00,
            )

        tax = st.number_input(
            "Tax (₹)",
            min_value=0.00,
            max_value=10_000_000.00,
            value=0.00,
            step=1.00,
        )


        subtotal = (
            float(quantity)
            * float(unit_price)
        )

        final_amount = (
            subtotal
            -
            float(discount)
            +
            float(tax)
        )


        st.divider()


        st.metric(
            "Merchant-Controlled Total",
            f"₹{max(final_amount, 0.0):,.2f}",
        )


        create_order_clicked = st.form_submit_button(
            "💳 Create Razorpay Order",
            use_container_width=True,
            type="primary",
        )


    if create_order_clicked:

        if not customer_name.strip():

            st.error(
                "Customer name is required."
            )

            st.stop()


        if not customer_email.strip():

            st.error(
                "Customer email is required."
            )

            st.stop()


        if "@" not in customer_email:

            st.error(
                "Please enter a valid customer email."
            )

            st.stop()


        if not customer_phone.strip():

            st.error(
                "Customer phone is required."
            )

            st.stop()


        if not product_name.strip():

            st.error(
                "Product name is required."
            )

            st.stop()


        if final_amount <= 0:

            st.error(
                "Order total must be greater than zero."
            )

            st.stop()


        final_description = (
            description.strip()
            if description.strip()
            else product_name.strip()
        )


        payload = {

            "amount":
                round(
                    final_amount,
                    2,
                ),

            "currency":
                "INR",

            "customer_name":
                customer_name.strip(),

            "customer_email":
                customer_email.strip(),

            "customer_phone":
                customer_phone.strip(),

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

            except Exception as exc:

                st.error(
                    "Unable to create Razorpay order."
                )

                st.code(
                    api_error_text(exc)
                )

                st.stop()


    created_order = (
        st.session_state.get(
            "last_created_order"
        )
    )


    if created_order:

        st.divider()

        st.markdown(
            "### ✅ Created Order"
        )


        order_id = (
            created_order.get(
                "order_id"
            )
        )


        amount_paise = int(
            created_order.get(
                "amount",
                0,
            )
            or 0
        )


        order_customer = (
            created_order.get(
                "customer",
                {},
            )
            or {}
        )


        o1, o2, o3 = st.columns(3)


        with o1:

            st.metric(
                "Order ID",
                order_id or "-",
            )


        with o2:

            st.metric(
                "Amount",
                f"₹{amount_paise / 100:,.2f}",
            )


        with o3:

            st.metric(
                "Status",
                created_order.get(
                    "status",
                    "CREATED",
                ),
            )


        st.write(
            f"**Customer:** "
            f"{order_customer.get('name') or '-'}"
        )

        st.write(
            f"**Email:** "
            f"{order_customer.get('email') or '-'}"
        )

        st.write(
            f"**Phone:** "
            f"{order_customer.get('phone') or '-'}"
        )

        st.write(
            f"**Description:** "
            f"{created_order.get('description') or '-'}"
        )


        if order_id:

            checkout_link = (
                f"{CHECKOUT_URL}"
                f"?order_id="
                f"{order_id}"
            )

            st.link_button(
                "💳 Open Customer Checkout",
                checkout_link,
                use_container_width=True,
            )


        with st.expander(
            "View created-order response"
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
        "💳 Merchant Payment Explorer"
        "</div>",
        unsafe_allow_html=True,
    )

    st.caption(
        "Search inside the table using the controls below. "
        "For large datasets, use the Order ID field to load "
        "one exact transaction."
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
    # PAYMENT VIEW
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
                "No merchant orders found."
            )

        else:

            orders_df = pd.DataFrame(
                merchant_orders
            ).copy()


            # ------------------------------------------------
            # Normalize
            # ------------------------------------------------

            expected_columns = [

                "order_id",
                "customer_name",
                "customer_email",
                "customer_phone",
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


            orders_df[
                "status"
            ] = (
                orders_df[
                    "status"
                ]
                .fillna(
                    "UNKNOWN"
                )
                .astype(str)
                .str.upper()
            )


            # =================================================
            # SEARCH
            # =================================================

            st.markdown(
                "### 🔎 Search"
            )


            search_term = st.text_input(

                "Order ID, Payment ID, Customer, "
                "Email, Phone or Description",

                placeholder=
                    "order_TWOWlLALvzYNWv",

                key=
                    "merchant_order_search",

            ).strip().lower()


            # =================================================
            # STATUS
            # =================================================

            status_options = sorted(
                orders_df[
                    "status"
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            )


            selected_status = st.multiselect(

                "Status",

                status_options,

                default=[],

                key=
                    "merchant_status_filter",

            )


            # =================================================
            # FILTER
            # =================================================

            filtered_orders = (
                orders_df.copy()
            )


            if search_term:

                search_columns = [

                    "order_id",
                    "customer_name",
                    "customer_email",
                    "customer_phone",
                    "payment_id",
                    "description",
                    "status",

                ]


                search_mask = pd.Series(
                    False,
                    index=
                        filtered_orders.index,
                )


                for column in search_columns:

                    values = (
                        filtered_orders[
                            column
                        ]
                        .fillna("")
                        .astype(str)
                        .str.lower()
                    )


                    search_mask = (
                        search_mask
                        |
                        values.str.contains(
                            search_term,
                            regex=False,
                            na=False,
                        )
                    )


                filtered_orders = (
                    filtered_orders[
                        search_mask
                    ]
                )


            if selected_status:

                filtered_orders = (
                    filtered_orders[
                        filtered_orders[
                            "status"
                        ]
                        .isin(
                            selected_status
                        )
                    ]
                )


            # =================================================
            # SUMMARY
            # =================================================

            s1, s2, s3, s4 = st.columns(4)


            with s1:

                st.metric(
                    "Total",
                    len(
                        orders_df
                    ),
                )


            with s2:

                st.metric(
                    "Matching",
                    len(
                        filtered_orders
                    ),
                )


            with s3:

                verified_count = int(
                    (
                        filtered_orders[
                            "status"
                        ]
                        ==
                        "VERIFIED"
                    ).sum()
                )

                st.metric(
                    "Verified",
                    verified_count,
                )


            with s4:

                visible_value = float(
                    pd.to_numeric(
                        filtered_orders[
                            "amount"
                        ],
                        errors="coerce",
                    )
                    .fillna(0)
                    .sum()
                )

                st.metric(
                    "Visible Value",
                    f"₹{visible_value:,.2f}",
                )


            # =================================================
            # DOWNLOAD
            # =================================================

            st.download_button(

                "📥 Download Filtered Orders",

                data=
                    filtered_orders.to_csv(
                        index=False
                    ),

                file_name=
                    "merchant_orders.csv",

                mime=
                    "text/csv",

                key=
                    "download_merchant_orders",

            )


            st.divider()


            # =================================================
            # LARGE DATA TABLE
            # =================================================

            st.markdown(
                "### 🛒 Merchant Orders"
            )


            display_columns = [

                "order_id",
                "customer_name",
                "customer_email",
                "amount",
                "currency",
                "status",
                "payment_id",
                "description",
                "created_at",
                "updated_at",

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
                    "No orders match your search/filter."
                )

            else:

                st.dataframe(

                    filtered_orders[
                        display_columns
                    ],

                    use_container_width=True,

                    height=550,

                    hide_index=True,

                )


            # =================================================
            # EXACT ORDER LOADER
            # =================================================

            st.divider()


            st.markdown(
                "### 🔎 Load Exact Order"
            )


            st.caption(
                "Paste the exact Order ID. This avoids relying "
                "on browser Ctrl+F or the rendered table."
            )


            existing_ids = [

                str(
                    value
                )

                for value
                in filtered_orders[
                    "order_id"
                ]
                .dropna()
                .tolist()

            ]


            default_order_id = ""


            if existing_ids:

                current_selected = (
                    st.session_state.get(
                        "loaded_order_id",
                        "",
                    )
                )


                if (
                    current_selected
                    in
                    existing_ids
                ):

                    default_order_id = (
                        current_selected
                    )


            exact_order_id = st.text_input(

                "Order ID",

                value=
                    default_order_id,

                placeholder=
                    "order_TWOWlLALvzYNWv",

                key=
                    "exact_order_id_input",

            ).strip()


            load_order_clicked = st.button(

                "📄 Load Order Details",

                key=
                    "load_exact_order",

                type=
                    "primary",

            )


            if load_order_clicked:

                if not exact_order_id:

                    st.error(
                        "Enter an Order ID."
                    )

                else:

                    st.session_state[
                        "loaded_order_id"
                    ] = exact_order_id


            loaded_order_id = (
                st.session_state.get(
                    "loaded_order_id"
                )
            )


            # =================================================
            # EXACT ORDER DETAILS
            # =================================================

            if loaded_order_id:

                st.divider()


                try:

                    exact_order_response = (
                        fetch_api(
                            "/merchant/orders/"
                            +
                            loaded_order_id
                        )
                    )


                    selected_order = (
                        exact_order_response.get(
                            "order"
                        )
                    )


                except Exception as exc:

                    selected_order = None

                    st.error(
                        "Unable to load this order."
                    )

                    st.code(
                        api_error_text(exc)
                    )


                if selected_order:

                    st.markdown(
                        "## 🧾 Complete Order Details"
                    )


                    selected_status = str(

                        selected_order.get(
                            "status",
                            "UNKNOWN",
                        )

                    ).upper()


                    order_amount = float(
                        selected_order.get(
                            "amount",
                            0,
                        )
                        or 0
                    )


                    payment_id = (
                        selected_order.get(
                            "payment_id"
                        )
                    )


                    # =========================================
                    # HEADER METRICS
                    # =========================================

                    d1, d2, d3, d4 = st.columns(4)


                    with d1:

                        st.metric(
                            "Amount",
                            f"₹{order_amount:,.2f}",
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
                                "order_id",
                                "-",
                            ),
                        )


                    with d4:

                        st.metric(
                            "Payment ID",
                            payment_id
                            or
                            "Not Paid",
                        )


                    # =========================================
                    # STATUS MESSAGE
                    # =========================================

                    if selected_status == "VERIFIED":

                        st.success(
                            "🟢 Payment verified successfully."
                        )

                    elif selected_status == "CAPTURED":

                        st.success(
                            "🟢 Payment captured."
                        )

                    elif selected_status == "AUTHORIZED":

                        st.warning(
                            "🟡 Payment authorized."
                        )

                    elif selected_status == "FAILED":

                        st.error(
                            "🔴 Payment failed."
                        )

                    elif selected_status == "CREATED":

                        st.info(
                            "⏳ Order created. "
                            "Payment has not been completed."
                        )

                    else:

                        st.warning(
                            f"Current status: {selected_status}"
                        )


                    # =========================================
                    # CUSTOMER
                    # =========================================

                    st.markdown(
                        "### 👤 Customer"
                    )


                    customer_cols = st.columns(3)


                    with customer_cols[0]:

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


                    with customer_cols[1]:

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


                    with customer_cols[2]:

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


                    # =========================================
                    # ORDER INFORMATION
                    # =========================================

                    st.markdown(
                        "### 🛍️ Order Information"
                    )


                    order_details = pd.DataFrame(
                        [

                            {

                                "Order ID":
                                    selected_order.get(
                                        "order_id"
                                    ),

                                "Description":
                                    selected_order.get(
                                        "description"
                                    ),

                                "Amount":
                                    (
                                        "₹"
                                        +
                                        f"{order_amount:,.2f}"
                                    ),

                                "Currency":
                                    selected_order.get(
                                        "currency"
                                    ),

                                "Status":
                                    selected_status,

                                "Payment ID":
                                    payment_id
                                    or
                                    "-",

                                "Created":
                                    selected_order.get(
                                        "created_at"
                                    ),

                                "Updated":
                                    selected_order.get(
                                        "updated_at"
                                    ),

                            }

                        ]
                    )


                    st.dataframe(

                        order_details,

                        use_container_width=True,

                        hide_index=True,

                    )


                    # =========================================
                    # CHECKOUT
                    # =========================================

                    if selected_status == "CREATED":

                        checkout_link = (

                            f"{CHECKOUT_URL}"
                            f"?order_id="
                            f"{selected_order.get('order_id')}"

                        )


                        st.link_button(

                            "💳 Open Customer Checkout",

                            checkout_link,

                            use_container_width=True,

                        )


                    # =========================================
                    # VERIFIED PAYMENT
                    # =========================================

                    related_verified = None


                    if payment_id:

                        related_verified = next(

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


                    st.markdown(
                        "### 🔐 Payment Details"
                    )


                    if related_verified:

                        payment_details = pd.DataFrame(
                            [

                                {

                                    "Payment ID":
                                        related_verified.get(
                                            "payment_id"
                                        ),

                                    "Order ID":
                                        related_verified.get(
                                            "order_id"
                                        ),

                                    "Amount":
                                        (
                                            "₹"
                                            +
                                            f"{float(related_verified.get('amount', 0) or 0):,.2f}"
                                        ),

                                    "Currency":
                                        related_verified.get(
                                            "currency"
                                        ),

                                    "Payment Method":
                                        related_verified.get(
                                            "payment_method"
                                        ),

                                    "Payment Status":
                                        related_verified.get(
                                            "payment_status"
                                        ),

                                    "Captured":
                                        (
                                            "YES"
                                            if
                                            related_verified.get(
                                                "captured"
                                            )
                                            else
                                            "NO"
                                        ),

                                    "Refunded":
                                        (
                                            "₹"
                                            +
                                            f"{float(related_verified.get('amount_refunded', 0) or 0):,.2f}"
                                        ),

                                    "Email":
                                        related_verified.get(
                                            "email"
                                        ),

                                    "Contact":
                                        related_verified.get(
                                            "contact"
                                        ),

                                }

                            ]
                        )


                        st.dataframe(

                            payment_details,

                            use_container_width=True,

                            hide_index=True,

                        )

                    else:

                        st.info(
                            "No verified payment record is "
                            "linked to this order."
                        )


                    # =========================================
                    # WEBHOOKS
                    # =========================================

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


                    # =========================================
                    # TIMELINE
                    # =========================================

                    st.markdown(
                        "### ⏱️ Payment Timeline"
                    )


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
                            "Signature Verified",
                            bool(
                                related_verified
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


                    for label, completed in timeline:

                        icon = (
                            "✅"
                            if completed
                            else
                            "⏳"
                        )


                        st.write(
                            f"{icon} **{label}**"
                        )


                    # =========================================
                    # WEBHOOK DETAILS
                    # =========================================

                    if related_webhooks:

                        st.markdown(
                            "### 🔔 Related Webhook Events"
                        )


                        st.dataframe(

                            pd.DataFrame(
                                related_webhooks
                            ),

                            use_container_width=True,

                            height=300,

                            hide_index=True,

                        )

                    else:

                        st.info(
                            "No webhook event is linked "
                            "to this payment yet."
                        )


                    # =========================================
                    # AI ANALYSIS
                    # =========================================

                    st.markdown(
                        "### 🤖 AI Analysis"
                    )


                    matching_decision = None


                    if payment_id:

                        matching_decision = next(

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
                                str(
                                    payment_id
                                )

                            ),

                            None,

                        )


                    if matching_decision:

                        ai1, ai2, ai3, ai4 = st.columns(4)


                        with ai1:

                            st.metric(
                                "Risk",
                                matching_decision.get(
                                    "risk_level"
                                )
                                or
                                "-",
                            )


                        with ai2:

                            st.metric(
                                "Risk Score",
                                (
                                    f"{float(matching_decision.get('risk_score', 0) or 0):.2f}"
                                ),
                            )


                        with ai3:

                            st.metric(
                                "Recovery",
                                (
                                    "₹"
                                    +
                                    f"{float(matching_decision.get('expected_recovery', 0) or 0):,.2f}"
                                ),
                            )


                        with ai4:

                            st.metric(
                                "Recommendation",
                                matching_decision.get(
                                    "final_action"
                                )
                                or
                                "-",
                            )


                        st.write(
                            "**Failure Reason:** "
                            f"{matching_decision.get('failure_reason') or '-'}"
                        )


                        st.write(
                            "**Decision Reason:** "
                            f"{matching_decision.get('decision_reason') or '-'}"
                        )


                        with st.expander(
                            "View complete AI decision"
                        ):

                            st.json(
                                matching_decision
                            )

                    else:

                        st.info(
                            "No AI decision is linked to this "
                            "payment. AI Recovery analyzes the "
                            "configured failed-payment dataset."
                        )


                    # =========================================
                    # RAW JSON
                    # =========================================

                    with st.expander(
                        "🔍 View complete order JSON"
                    ):

                        st.json(
                            selected_order
                        )


                elif load_order_clicked:

                    st.error(
                        "Order not found."
                    )


# ============================================================
# VERIFIED PAYMENTS VIEW
# ============================================================

    else:

        st.markdown(
            "### 🔐 Verified Razorpay Payments"
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

                "🔎 Search Payment ID, Order ID, "
                "Email or Contact",

                placeholder=
                    "pay_... / order_...",

                key=
                    "verified_search",

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


                search_mask = pd.Series(

                    False,

                    index=
                        verified_df.index,

                )


                for column in search_columns:

                    values = (
                        verified_df[
                            column
                        ]
                        .fillna("")
                        .astype(str)
                        .str.lower()
                    )


                    search_mask = (
                        search_mask
                        |
                        values.str.contains(
                            verified_search,
                            regex=False,
                            na=False,
                        )
                    )


                verified_df = (
                    verified_df[
                        search_mask
                    ]
                )


            st.download_button(

                "📥 Download Verified Payments",

                data=
                    verified_df.to_csv(
                        index=False
                    ),

                file_name=
                    "verified_payments.csv",

                mime=
                    "text/csv",

                key=
                    "download_verified_payments",

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


    if not decision_records:

        st.info(
            "No AI decisions available."
        )

    else:

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
                        float(
                            decision.get(
                                "amount",
                                0,
                            )
                            or 0
                        ),

                    "Failure":
                        decision.get(
                            "failure_reason"
                        ),

                    "Risk":
                        decision.get(
                            "risk_level"
                        ),

                    "Risk Score":
                        decision.get(
                            "risk_score"
                        ),

                    "Recovery Probability":
                        decision.get(
                            "recovery_probability"
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


        recovery_df = pd.DataFrame(
            recovery_rows
        )


        ai1, ai2, ai3 = st.columns(3)


        with ai1:

            action_filter = st.selectbox(
                "Action",
                [
                    "ALL",
                    "RETRY_NOW",
                    "RETRY_LATER",
                    "REVIEW",
                    "DO_NOTHING",
                ],
                key="recovery_action_filter",
            )


        with ai2:

            risk_filter = st.selectbox(
                "Risk",
                [
                    "ALL",
                    "LOW",
                    "MEDIUM",
                    "HIGH",
                ],
                key="recovery_risk_filter",
            )


        with ai3:

            min_recovery = st.number_input(
                "Minimum Expected Recovery (₹)",
                min_value=0.0,
                value=0.0,
                step=100.0,
                key="recovery_min_value",
            )


        filtered_recovery = (
            recovery_df.copy()
        )


        if action_filter != "ALL":

            filtered_recovery = (
                filtered_recovery[
                    filtered_recovery[
                        "Decision"
                    ]
                    ==
                    action_filter
                ]
            )


        if risk_filter != "ALL":

            filtered_recovery = (
                filtered_recovery[
                    filtered_recovery[
                        "Risk"
                    ]
                    ==
                    risk_filter
                ]
            )


        filtered_recovery = (
            filtered_recovery[
                filtered_recovery[
                    "Expected Recovery"
                ]
                >=
                min_recovery
            ]
        )


        st.dataframe(
            filtered_recovery,
            use_container_width=True,
            height=550,
            hide_index=True,
        )


        st.divider()


        # ----------------------------------------------------
        # EXPLAINABILITY
        # ----------------------------------------------------

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

        ]


        selected_ai_payment = st.selectbox(

            "Select Payment",

            payment_options,

            key=
                "ai_selected_payment",

        )


        selected_ai_decision = next(

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
                selected_ai_payment

            ),

            decision_records[0],

        )


        policy = (
            selected_ai_decision.get(
                "policy",
                {},
            )
            or {}
        )


        d1, d2, d3, d4 = st.columns(4)


        with d1:

            st.metric(
                "Amount",
                (
                    "₹"
                    +
                    f"{float(selected_ai_decision.get('amount', 0) or 0):,.2f}"
                ),
            )


        with d2:

            st.metric(
                "Risk Score",
                (
                    f"{float(selected_ai_decision.get('risk_score', 0) or 0):.2f}"
                ),
            )


        with d3:

            st.metric(
                "Expected Recovery",
                (
                    "₹"
                    +
                    f"{float(selected_ai_decision.get('expected_recovery', 0) or 0):,.2f}"
                ),
            )


        with d4:

            confidence = float(
                selected_ai_decision.get(
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
            f"{selected_ai_decision.get('payment_id')}"
        )


        st.write(
            "**Order:** "
            f"{selected_ai_decision.get('order_id')}"
        )


        st.write(
            "**Customer:** "
            f"{selected_ai_decision.get('customer_id')}"
        )


        st.write(
            "**Payment Method:** "
            f"{selected_ai_decision.get('payment_method')}"
        )


        st.write(
            "**Failure Reason:** "
            f"{selected_ai_decision.get('failure_reason')}"
        )


        st.write(
            "**Final Decision:** "
            f"{selected_ai_decision.get('final_action')}"
        )


        st.write(
            "**Decision Reason:** "
            f"{selected_ai_decision.get('decision_reason')}"
        )


        st.write(
            "**Policy Mode:** "
            f"{policy.get('execution_mode')}"
        )


        st.markdown(
            "### 🧪 Simulation Scenarios"
        )


        scenarios = (
            selected_ai_decision.get(
                "simulation_scenarios",
                [],
            )
        )


        if scenarios:

            st.dataframe(
                pd.DataFrame(
                    scenarios
                ),
                use_container_width=True,
                hide_index=True,
            )

        else:

            st.info(
                "No simulation scenarios available."
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
                    decision.get(
                        "amount"
                    ),

                "Risk":
                    decision.get(
                        "risk_level"
                    ),

                "Expected Recovery":
                    decision.get(
                        "expected_recovery"
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
            f"{len(approval_rows)} decision(s) "
            "require merchant approval."
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
            "Approval controls are test/demo controls. "
            "No live financial action is executed directly."
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
        "🔔 Razorpay Webhook Monitor"
        "</div>",
        unsafe_allow_html=True,
    )


    w1, w2, w3 = st.columns(3)


    with w1:

        st.metric(
            "Webhook Events",
            int(
                activity_data.get(
                    "webhook_events",
                    0,
                )
            ),
        )


    with w2:

        st.metric(
            "Webhook Processing",
            int(
                activity_data.get(
                    "webhook_processing",
                    0,
                )
            ),
        )


    with w3:

        st.metric(
            "Verified Payments",
            int(
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
            "🔎 Search webhook",
            key="webhook_search",
        ).strip().lower()


        if webhook_search:

            mask = (

                webhook_df.astype(
                    str
                )
                .apply(
                    lambda column:
                        column
                        .str
                        .lower()
                        .str
                        .contains(
                            webhook_search,
                            regex=False,
                            na=False,
                        )
                )
                .any(
                    axis=1
                )
            )


            webhook_df = webhook_df[
                mask
            ]


        st.dataframe(

            webhook_df.head(100),

            use_container_width=True,

            height=500,

            hide_index=True,

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
        "📋 Audit Explorer"
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


        event_filter = st.multiselect(
            "Event Type",
            sorted(
                audit_df[
                    "Event"
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            ),
            default=[],
            key="audit_event_filter",
        )


        audit_status_filter = st.multiselect(
            "Status",
            sorted(
                audit_df[
                    "Status"
                ]
                .dropna()
                .astype(str)
                .unique()
                .tolist()
            ),
            default=[],
            key="audit_status_filter",
        )


        filtered_audit = (
            audit_df.copy()
        )


        if event_filter:

            filtered_audit = (
                filtered_audit[
                    filtered_audit[
                        "Event"
                    ]
                    .astype(str)
                    .isin(
                        event_filter
                    )
                ]
            )


        if audit_status_filter:

            filtered_audit = (
                filtered_audit[
                    filtered_audit[
                        "Status"
                    ]
                    .astype(str)
                    .isin(
                        audit_status_filter
                    )
                ]
            )


        st.dataframe(

            filtered_audit,

            use_container_width=True,

            height=600,

            hide_index=True,

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
Server-side Order Creation
    ↓
Razorpay Create Order
    ↓
Razorpay Checkout
    ↓
CUSTOMER PAYMENT
    ↓
┌──────────────────────────┐
│ Checkout Verification    │
│            +             │
│ Razorpay Webhook         │
└────────────┬─────────────┘
             ↓
         PostgreSQL
             ↓
       MerchantOps AI
             ↓
 Revenue → Risk → Simulation
             ↓
       Decision Agent
             ↓
        Governance
             ↓
      Merchant Dashboard
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