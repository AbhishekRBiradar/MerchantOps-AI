from __future__ import annotations

import json
import os
import uuid
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
# THEME STATE
# ============================================================

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"

theme_mode = st.session_state["theme_mode"]


# ============================================================
# STYLING
# ============================================================

# Theme-specific CSS is generated first and the final theme
# overrides are placed AFTER the shared styling so they win
# over any generic dark-mode declarations.

if theme_mode == "dark":

    theme_css = """
    :root {
        --mo-bg: #080c16;
        --mo-bg-2: #0d1322;
        --mo-surface: rgba(255,255,255,0.055);
        --mo-surface-strong: rgba(255,255,255,0.085);
        --mo-border: rgba(255,255,255,0.11);
        --mo-border-hover: rgba(255,255,255,0.22);
        --mo-text: #f8fafc;
        --mo-muted: #94a3b8;
        --mo-accent: #7c83ff;
        --mo-accent-2: #a78bfa;
        --mo-success: #22c55e;
        --mo-warning: #f59e0b;
        --mo-danger: #ef4444;
        --mo-shadow: 0 20px 60px rgba(0,0,0,0.28);
    }

    .stApp {
        background:
            radial-gradient(
                circle at 5% 0%,
                rgba(124,131,255,0.13),
                transparent 25%
            ),
            radial-gradient(
                circle at 95% 8%,
                rgba(167,139,250,0.10),
                transparent 23%
            ),
            radial-gradient(
                circle at 50% 100%,
                rgba(59,130,246,0.07),
                transparent 30%
            ),
            var(--mo-bg) !important;

        color: var(--mo-text) !important;
    }

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                rgba(15,23,42,0.90),
                rgba(2,6,23,0.96)
            ) !important;
    }

    section[data-testid="stSidebar"] pre,
    section[data-testid="stSidebar"] code {
        color: #e2e8f0 !important;
    }

    section[data-testid="stSidebar"] pre {
        background:
            rgba(255,255,255,0.055) !important;
        border:
            1px solid rgba(255,255,255,0.10) !important;
        border-radius:
            12px !important;
    }

    div[data-testid="stStatusWidget"] {
        background:
            rgba(15,23,42,0.92) !important;
        color:
            #f8fafc !important;
        border-radius:
            12px !important;
    }
    """

else:

    theme_css = """
    :root {
        --mo-bg: #eef2f8;
        --mo-bg-2: #f8fafc;
        --mo-surface: rgba(255,255,255,0.68);
        --mo-surface-strong: rgba(255,255,255,0.86);
        --mo-border: rgba(15,23,42,0.10);
        --mo-border-hover: rgba(79,70,229,0.25);
        --mo-text: #0f172a;
        --mo-muted: #64748b;
        --mo-accent: #4f46e5;
        --mo-accent-2: #7c3aed;
        --mo-success: #16a34a;
        --mo-warning: #d97706;
        --mo-danger: #dc2626;
        --mo-shadow: 0 18px 50px rgba(15,23,42,0.10);
    }

    .stApp {
        background:
            radial-gradient(
                circle at 5% 0%,
                rgba(99,102,241,0.12),
                transparent 25%
            ),
            radial-gradient(
                circle at 95% 8%,
                rgba(124,58,237,0.09),
                transparent 24%
            ),
            linear-gradient(
                180deg,
                #f8fafc 0%,
                #eef2f8 100%
            ) !important;

        color:
            var(--mo-text) !important;
    }

    .stApp p,
    .stApp span,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color:
            var(--mo-text);
    }

    .stApp small,
    .stApp [data-testid="stCaptionContainer"],
    .stApp .stCaption {
        color:
            var(--mo-muted) !important;
    }

    /* ---------- Sidebar ---------- */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                rgba(255,255,255,0.94),
                rgba(241,245,249,0.96)
            ) !important;

        border-right:
            1px solid rgba(15,23,42,0.09) !important;

        box-shadow:
            8px 0 30px rgba(15,23,42,0.06) !important;
    }

    section[data-testid="stSidebar"] * {
        color:
            #0f172a;
    }

    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
        color:
            #64748b !important;
    }

    /* ---------- Sidebar code boxes ---------- */

    section[data-testid="stSidebar"] pre {
        background:
            #ffffff !important;

        color:
            #0f172a !important;

        border:
            1px solid rgba(15,23,42,0.10) !important;

        border-radius:
            12px !important;

        box-shadow:
            0 8px 24px rgba(15,23,42,0.06) !important;
    }

    section[data-testid="stSidebar"] pre code,
    section[data-testid="stSidebar"] code {
        background:
            transparent !important;

        color:
            #0f172a !important;

        text-shadow:
            none !important;
    }

    /* ---------- Main metrics ---------- */

    div[data-testid="stMetric"] {
        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.90),
                rgba(255,255,255,0.68)
            ) !important;

        border:
            1px solid rgba(15,23,42,0.09) !important;

        box-shadow:
            0 12px 35px rgba(15,23,42,0.08) !important;
    }

    div[data-testid="stMetricLabel"] {
        color:
            #64748b !important;
    }

    div[data-testid="stMetricValue"] {
        color:
            #0f172a !important;
    }

    /* ---------- Buttons ---------- */

    .stButton > button,
    .stLinkButton > a,
    .stDownloadButton > button {
        background:
            rgba(255,255,255,0.78) !important;

        color:
            #0f172a !important;

        border:
            1px solid rgba(15,23,42,0.10) !important;

        box-shadow:
            0 8px 22px rgba(15,23,42,0.07) !important;
    }

    .stButton > button:hover,
    .stLinkButton > a:hover,
    .stDownloadButton > button:hover {
        background:
            rgba(255,255,255,0.96) !important;

        border-color:
            rgba(79,70,229,0.30) !important;
    }

    /* ---------- Inputs ---------- */

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div,
    textarea {
        background:
            rgba(255,255,255,0.86) !important;

        color:
            #0f172a !important;

        border-color:
            rgba(15,23,42,0.10) !important;
    }

    /* ---------- Alerts ---------- */

    div[data-testid="stAlert"] {
        box-shadow:
            0 10px 28px rgba(15,23,42,0.06) !important;
    }

    /* ---------- Tables ---------- */

    div[data-testid="stDataFrame"] {
        background:
            rgba(255,255,255,0.75) !important;

        border:
            1px solid rgba(15,23,42,0.09) !important;

        box-shadow:
            0 14px 35px rgba(15,23,42,0.07) !important;
    }

    /* ---------- Expanders ---------- */

    details {
        background:
            rgba(255,255,255,0.68) !important;

        border:
            1px solid rgba(15,23,42,0.09) !important;
    }

    details summary {
        color:
            #0f172a !important;
    }

    /* ---------- Status / Running widget ---------- */

    div[data-testid="stStatusWidget"] {
        background:
            rgba(255,255,255,0.94) !important;

        color:
            #0f172a !important;

        border:
            1px solid rgba(15,23,42,0.10) !important;

        border-radius:
            12px !important;

        box-shadow:
            0 12px 35px rgba(15,23,42,0.12) !important;
    }

    div[data-testid="stStatusWidget"] *,
    div[data-testid="stStatusWidget"] code {
        color:
            #0f172a !important;

        background:
            transparent !important;
    }

    /* ---------- Sidebar radio / toggle ---------- */

    section[data-testid="stSidebar"] [role="radiogroup"] label,
    section[data-testid="stSidebar"] [data-testid="stToggle"] label {
        color:
            #0f172a !important;
    }
    """


st.markdown(
    f"""
    <style>

    html {{
        scroll-behavior: smooth;
    }}

    body {{
        overflow-x: hidden;
    }}

    .block-container {{
        width: 100% !important;
        max-width: none !important;
        padding-top: 1.5rem !important;
        padding-left: clamp(1rem, 2vw, 2.5rem) !important;
        padding-right: clamp(1rem, 2vw, 2.5rem) !important;
        padding-bottom: 5rem !important;
    }}

    .stApp {{
        color: var(--mo-text);
    }}

    .main-title {{
        font-size: clamp(32px, 4vw, 48px);
        font-weight: 850;
        letter-spacing: -2px;
        margin-bottom: 4px;
        animation: moFadeDown 0.55s ease-out;
    }}

    .subtitle {{
        font-size: 15px;
        color: var(--mo-muted);
        margin-bottom: 22px;
        animation: moFadeUp 0.65s ease-out;
    }}

    .section-title {{
        font-size: clamp(23px, 2.3vw, 30px);
        font-weight: 800;
        letter-spacing: -0.7px;
        margin-top: 10px;
        margin-bottom: 10px;
    }}

    /* =====================================================
       GLASS METRICS
       ===================================================== */

    div[data-testid="stMetric"] {{
        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.075),
                rgba(255,255,255,0.025)
            );

        backdrop-filter:
            blur(18px) saturate(150%);

        -webkit-backdrop-filter:
            blur(18px) saturate(150%);

        border:
            1px solid var(--mo-border);

        border-radius:
            18px;

        padding:
            16px 18px;

        box-shadow:
            var(--mo-shadow);

        transition:
            transform 0.22s ease,
            box-shadow 0.22s ease,
            border-color 0.22s ease;
    }}

    div[data-testid="stMetric"]:hover {{
        transform:
            translateY(-5px) scale(1.01);

        border-color:
            rgba(124,131,255,0.36);

        box-shadow:
            0 26px 70px rgba(0,0,0,0.20);
    }}

    div[data-testid="stMetricLabel"] {{
        color:
            var(--mo-muted);
    }}

    /* =====================================================
       BUTTONS
       ===================================================== */

    .stButton > button,
    .stLinkButton > a,
    .stDownloadButton > button {{
        border-radius:
            12px !important;

        border:
            1px solid var(--mo-border) !important;

        background:
            rgba(255,255,255,0.045) !important;

        backdrop-filter:
            blur(12px);

        -webkit-backdrop-filter:
            blur(12px);

        font-weight:
            750 !important;

        transition:
            transform 0.18s ease,
            box-shadow 0.18s ease,
            border-color 0.18s ease;
    }}

    .stButton > button:hover,
    .stLinkButton > a:hover,
    .stDownloadButton > button:hover {{
        transform:
            translateY(-2px);

        box-shadow:
            0 12px 30px rgba(0,0,0,0.18);
    }}

    /* =====================================================
       ALERTS
       ===================================================== */

    div[data-testid="stAlert"] {{
        border-radius:
            16px !important;

        backdrop-filter:
            blur(14px);

        -webkit-backdrop-filter:
            blur(14px);

        animation:
            moFadeUp 0.4s ease-out;
    }}

    /* =====================================================
       TABS
       ===================================================== */

    button[data-baseweb="tab"] {{
        border-radius:
            10px 10px 0 0;

        font-weight:
            750;

        transition:
            transform 0.18s ease,
            color 0.18s ease;
    }}

    button[data-baseweb="tab"]:hover {{
        transform:
            translateY(-2px);
    }}

    /* =====================================================
       TABLES
       ===================================================== */

    div[data-testid="stDataFrame"] {{
        border:
            1px solid var(--mo-border);

        border-radius:
            16px;

        overflow:
            hidden;

        box-shadow:
            0 15px 45px rgba(0,0,0,0.12);
    }}

    /* =====================================================
       EXPANDERS
       ===================================================== */

    details {{
        border:
            1px solid var(--mo-border) !important;

        border-radius:
            14px !important;

        background:
            rgba(255,255,255,0.025);

        backdrop-filter:
            blur(12px);
    }}

    /* =====================================================
       SCROLL BUTTONS
       ===================================================== */

    .mo-scroll-controls {{
        position: fixed;
        right: 24px;
        bottom: 24px;
        z-index: 999999;

        display:
            flex;

        flex-direction:
            column;

        gap:
            9px;
    }}

    .mo-scroll-btn {{
        width:
            44px;

        height:
            44px;

        display:
            flex;

        align-items:
            center;

        justify-content:
            center;

        border-radius:
            50%;

        text-decoration:
            none !important;

        color:
            var(--mo-text) !important;

        background:
            rgba(255,255,255,0.075);

        border:
            1px solid
            rgba(255,255,255,0.16);

        backdrop-filter:
            blur(18px) saturate(150%);

        -webkit-backdrop-filter:
            blur(18px) saturate(150%);

        box-shadow:
            0 12px 35px rgba(0,0,0,0.30);

        font-size:
            20px;

        font-weight:
            800;

        transition:
            transform 0.2s ease,
            background 0.2s ease,
            box-shadow 0.2s ease;
    }}

    .mo-scroll-btn:hover {{
        transform:
            translateY(-4px);

        background:
            rgba(124,131,255,0.20);

        box-shadow:
            0 18px 42px rgba(0,0,0,0.35);
    }}

    /* =====================================================
       ANIMATIONS
       ===================================================== */

    @keyframes moFadeUp {{

        from {{
            opacity: 0;
            transform: translateY(12px);
        }}

        to {{
            opacity: 1;
            transform: translateY(0);
        }}

    }}

    @keyframes moFadeDown {{

        from {{
            opacity: 0;
            transform: translateY(-12px);
        }}

        to {{
            opacity: 1;
            transform: translateY(0);
        }}

    }}

    @media (max-width: 900px) {{

        .main-title {{
            font-size:
                34px;
        }}

        .subtitle {{
            font-size:
                14px;
        }}

        .mo-scroll-controls {{
            right:
                14px;

            bottom:
                14px;
        }}

        .mo-scroll-btn {{
            width:
                40px;

            height:
                40px;
        }}

    }}

    @media (prefers-reduced-motion: reduce) {{

        *,
        *::before,
        *::after {{

            animation:
                none !important;

            transition:
                none !important;

            scroll-behavior:
                auto !important;
        }}

    }}

    /* =====================================================
       FINAL THEME OVERRIDES
       ===================================================== */

    {theme_css}

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# FINAL THEME OVERRIDES
# ============================================================

if theme_mode == "dark":

    final_theme_css = """
    <style>

    /* =====================================================
       DARK MODE
       ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 5% 0%,
                rgba(124,131,255,0.13),
                transparent 25%
            ),
            radial-gradient(
                circle at 95% 8%,
                rgba(167,139,250,0.10),
                transparent 23%
            ),
            #080c16 !important;

        color: #f8fafc !important;
    }

    /* Main text */

    .stApp p,
    .stApp span,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color: #f8fafc;
    }

    /* Captions */

    [data-testid="stCaptionContainer"] {
        color: #94a3b8 !important;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                rgba(15,23,42,0.96),
                rgba(2,6,23,0.99)
            ) !important;

        border-right:
            1px solid
            rgba(255,255,255,0.10) !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {
        color: #f8fafc !important;
    }

    section[data-testid="stSidebar"]
    [data-testid="stCaptionContainer"] {
        color: #94a3b8 !important;
    }

    /* Sidebar code */

    section[data-testid="stSidebar"] pre,
    section[data-testid="stSidebar"] code {
        color: #e2e8f0 !important;
        background: #111827 !important;
    }

    section[data-testid="stSidebar"] pre {
        border:
            1px solid
            rgba(255,255,255,0.10) !important;
        border-radius: 12px !important;
    }

    /* Tabs */

    button[data-baseweb="tab"] {
        color: #cbd5e1 !important;
        background: transparent !important;
    }

    button[data-baseweb="tab"]:hover {
        color: #ffffff !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #a5b4fc !important;
        font-weight: 800 !important;
    }

    /* Dividers */

    hr {
        border-color:
            rgba(255,255,255,0.12) !important;
        opacity: 1 !important;
    }

    /* Inputs */

    div[data-baseweb="input"] input,
    textarea {
        color: #f8fafc !important;
        background: #111827 !important;
        caret-color: #ffffff !important;
    }

    /* Selects */

    div[data-baseweb="select"] * {
        color: #f8fafc !important;
    }

    /* Streamlit code blocks */

    div[data-testid="stCode"] {
        background:
            rgba(255,255,255,0.045) !important;

        border:
            1px solid
            rgba(255,255,255,0.09) !important;

        border-radius:
            12px !important;
    }

    div[data-testid="stCode"] pre,
    div[data-testid="stCode"] code {
        color: #e2e8f0 !important;
        background: transparent !important;
    }

    /* Running / status widget */

    div[data-testid="stStatusWidget"] {
        background:
            rgba(15,23,42,0.94) !important;

        color:
            #f8fafc !important;

        border:
            1px solid
            rgba(255,255,255,0.10) !important;

        border-radius:
            12px !important;
    }

    div[data-testid="stStatusWidget"] * {
        color:
            #f8fafc !important;
    }

    /* Metrics */

    div[data-testid="stMetricLabel"] {
        color:
            #94a3b8 !important;
    }

    div[data-testid="stMetricValue"] {
        color:
            #f8fafc !important;
    }

    /* Tables */

    div[data-testid="stDataFrame"] {
        border-color:
            rgba(255,255,255,0.10) !important;
    }

    </style>
    """

else:

    final_theme_css = """
    <style>

    /* =====================================================
       LIGHT MODE
       ===================================================== */

    .stApp {
        background:
            radial-gradient(
                circle at 5% 0%,
                rgba(99,102,241,0.10),
                transparent 25%
            ),
            radial-gradient(
                circle at 95% 8%,
                rgba(124,58,237,0.08),
                transparent 23%
            ),
            linear-gradient(
                180deg,
                #f8fafc 0%,
                #eef2f7 100%
            ) !important;

        color:
            #0f172a !important;
    }

    /* Main text */

    .stApp p,
    .stApp span,
    .stApp label,
    .stApp h1,
    .stApp h2,
    .stApp h3,
    .stApp h4,
    .stApp h5,
    .stApp h6 {
        color: #0f172a !important;
    }

    /* Captions */

    [data-testid="stCaptionContainer"] {
        color: #64748b !important;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background:
            linear-gradient(
                180deg,
                rgba(255,255,255,0.98),
                rgba(241,245,249,0.99)
            ) !important;

        border-right:
            1px solid
            rgba(15,23,42,0.09) !important;

        box-shadow:
            8px 0 30px
            rgba(15,23,42,0.05) !important;
    }

    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h4,
    section[data-testid="stSidebar"] h5,
    section[data-testid="stSidebar"] h6 {
        color: #0f172a !important;
    }

    section[data-testid="stSidebar"]
    [data-testid="stCaptionContainer"] {
        color: #64748b !important;
    }

    /* Sidebar code */

    section[data-testid="stSidebar"] pre {
        background:
            #ffffff !important;

        color:
            #0f172a !important;

        border:
            1px solid
            rgba(15,23,42,0.10) !important;

        border-radius:
            12px !important;

        box-shadow:
            0 8px 22px
            rgba(15,23,42,0.06) !important;
    }

    section[data-testid="stSidebar"] pre code,
    section[data-testid="stSidebar"] code {
        background:
            transparent !important;

        color:
            #0f172a !important;

        text-shadow:
            none !important;
    }

    /* Tabs */

    button[data-baseweb="tab"] {
        color:
            #64748b !important;

        background:
            transparent !important;
    }

    button[data-baseweb="tab"]:hover {
        color:
            #334155 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color:
            #4f46e5 !important;

        font-weight:
            800 !important;
    }

    /* Tab content */

    [data-baseweb="tab-panel"] {
        color:
            #0f172a !important;
    }

    /* Dividers */

    hr {
        border-color:
            rgba(15,23,42,0.12) !important;

        opacity:
            1 !important;
    }

    /* Inputs */

    div[data-baseweb="input"] input,
    textarea {
        color:
            #0f172a !important;

        background:
            #ffffff !important;

        caret-color:
            #0f172a !important;
    }

    /* Selects */

    div[data-baseweb="select"] * {
        color:
            #0f172a !important;
    }

    /* Code blocks */

    div[data-testid="stCode"] {
        background:
            rgba(255,255,255,0.82) !important;

        border:
            1px solid
            rgba(15,23,42,0.10) !important;

        border-radius:
            12px !important;

        box-shadow:
            0 8px 24px
            rgba(15,23,42,0.05) !important;
    }

    div[data-testid="stCode"] pre,
    div[data-testid="stCode"] code {
        color:
            #0f172a !important;

        background:
            transparent !important;

        text-shadow:
            none !important;
    }

    /* Running / status widget */

    div[data-testid="stStatusWidget"] {
        background:
            rgba(255,255,255,0.96) !important;

        color:
            #0f172a !important;

        border:
            1px solid
            rgba(15,23,42,0.10) !important;

        border-radius:
            12px !important;

        box-shadow:
            0 12px 35px
            rgba(15,23,42,0.10) !important;
    }

    div[data-testid="stStatusWidget"] * {
        color:
            #0f172a !important;
    }

    /* Metrics */

    div[data-testid="stMetricLabel"] {
        color:
            #64748b !important;
    }

    div[data-testid="stMetricValue"] {
        color:
            #0f172a !important;
    }

    /* Tables */

    div[data-testid="stDataFrame"] {
        border:
            1px solid
            rgba(15,23,42,0.10) !important;

        box-shadow:
            0 12px 30px
            rgba(15,23,42,0.06) !important;
    }

    </style>
    """


st.markdown(
    final_theme_css,
    unsafe_allow_html=True,
)

def create_buyer_cart() -> str:

    response = post_api(
        "/cart"
    )

    cart = (
        response.get(
            "cart",
            {},
        )
        or {}
    )

    cart_id = cart.get(
        "cart_id"
    )

    if not cart_id:
        raise ValueError(
            "Buyer cart was not created."
        )

    return str(
        cart_id
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


def put_api(
    endpoint: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    response = requests.put(
        f"{API_URL}{endpoint}",
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def patch_api(
    endpoint: str,
    payload: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:

    response = requests.patch(
        f"{API_URL}{endpoint}",
        json=payload,
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def delete_api(
    endpoint: str,
) -> Dict[str, Any]:

    response = requests.delete(
        f"{API_URL}{endpoint}",
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def fetch_cart_direct(
    cart_id: str,
) -> Dict[str, Any]:

    response = requests.get(
        f"{API_URL}/cart/{cart_id}",
        timeout=60,
    )

    response.raise_for_status()

    return response.json()


def create_buyer_cart() -> str:

    response = post_api(
        "/cart"
    )

    cart = (
        response.get(
            "cart",
            {},
        )
        or {}
    )

    cart_id = cart.get(
        "cart_id"
    )

    if not cart_id:
        raise ValueError(
            "Buyer cart was not created."
        )

    return str(
        cart_id
    )


# ============================================================
# SECTION DATA LOADERS
# ============================================================

@st.cache_data(ttl=30)
def get_payments_data(
    source: str,
) -> Dict[str, Any]:

    return fetch_api(
        f"/payments?source={source}"
    )


@st.cache_data(ttl=30)
def get_analysis_data(
    source: str,
) -> Dict[str, Any]:

    return fetch_api(
        f"/analyze?source={source}"
    )


@st.cache_data(ttl=30)
def get_decisions_data(
    source: str,
) -> Dict[str, Any]:

    return fetch_api(
        f"/decisions?source={source}"
    )


@st.cache_data(ttl=30)
def get_activity_data() -> Dict[str, Any]:

    return fetch_api(
        "/activity/stats"
    )


@st.cache_data(ttl=30)
def get_audit_data() -> Dict[str, Any]:

    return fetch_api(
        "/audit?limit=1000"
    )


@st.cache_data(ttl=30)
def get_webhook_data() -> Dict[str, Any]:

    return fetch_api(
        "/webhooks/events"
    )


@st.cache_data(ttl=30)
def get_verified_data() -> Dict[str, Any]:

    return fetch_api(
        "/payments/verified"
    )


@st.cache_data(ttl=30)
def get_merchant_orders_data() -> Dict[str, Any]:

    return fetch_api(
        "/merchant/orders"
    )


@st.cache_data(ttl=30)
def get_catalog_data() -> Dict[str, Any]:

    return fetch_api(
        "/catalog"
    )

# ============================================================
# VALUE HELPERS
# ============================================================

def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:

    try:

        if value is None or value == "":
            return default

        return float(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def safe_int(
    value: Any,
    default: int = 0,
) -> int:

    try:

        if value is None or value == "":
            return default

        return int(value)

    except (
        TypeError,
        ValueError,
    ):

        return default


def format_inr(
    value: Any,
) -> str:

    return (
        f"₹{safe_float(value):,.2f}"
    )


def normalize_status(
    value: Any,
) -> str:

    return str(
        value or "UNKNOWN"
    ).upper()


# ============================================================
# SESSION STATE
# ============================================================

if "last_created_order" not in st.session_state:
    st.session_state["last_created_order"] = None

if "loaded_order_id" not in st.session_state:
    st.session_state["loaded_order_id"] = ""

if "payment_view" not in st.session_state:
    st.session_state["payment_view"] = "Merchant Orders"

if "buyer_session_id" not in st.session_state:
    st.session_state["buyer_session_id"] = f"buyer_{uuid.uuid4().hex[:12]}"

if "buyer_cart_id" not in st.session_state:
    st.session_state["buyer_cart_id"] = None

if "buyer_messages" not in st.session_state:
    st.session_state["buyer_messages"] = []

if "buyer_current_cart" not in st.session_state:
    st.session_state["buyer_current_cart"] = None

if "buyer_selected_product" not in st.session_state:
    st.session_state["buyer_selected_product"] = None

if "buyer_last_response" not in st.session_state:
    st.session_state["buyer_last_response"] = None

# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div id="mo-top"></div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="mo-scroll-controls">
        <a class="mo-scroll-btn" href="#mo-top" title="Go to top">↑</a>
        <a class="mo-scroll-btn" href="#mo-bottom" title="Go to bottom">↓</a>
    </div>
    """,
    unsafe_allow_html=True,
)


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

    # ========================================================
    # APPEARANCE
    # ========================================================

    st.markdown("### 🎨 Appearance")

    dark_mode = st.toggle(
        "🌙 Dark Mode",
        value=(
            st.session_state["theme_mode"]
            ==
            "dark"
        ),
        key="dashboard_theme_toggle",
    )

    selected_theme = (
        "dark"
        if dark_mode
        else "light"
    )

    if (
        selected_theme
        !=
        st.session_state["theme_mode"]
    ):

        st.session_state["theme_mode"] = (
            selected_theme
        )

        st.rerun()

    st.caption(
        "Current theme: "
        + (
            "Dark"
            if st.session_state["theme_mode"] == "dark"
            else "Light"
        )
    )

    st.caption(
        "Switch the dashboard between dark glass and light glass."
    )

    st.divider()

    # ========================================================
    # PAYMENT DATA SOURCE
    # ========================================================

    st.markdown(
        "### 💳 Payment Data Source"
    )

    payment_source_label = st.radio(
        "Payment Data Source",
        [
            "Demo Dataset",
            "Razorpay Test Mode",
        ],
        index=0,
        label_visibility="collapsed",
    )

    payment_source = (
        "razorpay"
        if payment_source_label
        ==
        "Razorpay Test Mode"
        else
        "csv"
    )

    # ========================================================
    # REFRESH
    # ========================================================

    if st.button(
        "🔄 Refresh All Data",
        use_container_width=True,
        key="sidebar_refresh_all",
    ):

        st.cache_data.clear()

        st.rerun()

    st.divider()

    # ========================================================
    # BACKEND
    # ========================================================

    st.markdown(
        "### 🌐 Backend"
    )

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

    # ========================================================
    # CUSTOMER CHECKOUT
    # ========================================================

    st.markdown(
        "### 🛒 Customer Checkout"
    )

    st.code(
        CHECKOUT_URL,
        language="text",
    )

    st.caption(
        "Customer payment page"
    )

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
        "🛍️ Catalog",
        "🤖 Buyer AI",
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

    try:

        payments_data = get_payments_data(
            payment_source
        )

        analysis_data = get_analysis_data(
            payment_source
        )

        decisions_data = get_decisions_data(
            payment_source
        )

        activity_data = get_activity_data()

        verified_data = get_verified_data()

        merchant_orders_data = (
            get_merchant_orders_data()
        )

        verified_payments = (
            verified_data.get(
                "payments",
                [],
            )
            or []
        )

        merchant_orders = (
            merchant_orders_data.get(
                "orders",
                [],
            )
            or []
        )

        decision_records = (
            decisions_data.get(
                "decisions",
                [],
            )
            or []
        )

    except Exception as exc:

        st.error(
            "❌ Unable to load Overview data."
        )

        st.code(
            str(exc)
        )

        st.stop()

    # YOUR EXISTING OVERVIEW CODE CONTINUES HERE

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
# TAB 3 — CATALOG
# ============================================================

with tabs[2]:

    try:

        catalog_response = get_catalog_data()

        catalog_products = (
            catalog_response.get(
                "products",
                [],
            )
            or []
        )

        catalog_summary_data = (
            catalog_response.get(
                "summary",
                {},
            )
            or {}
        )

    except Exception as exc:

        st.error(
            "❌ Unable to load Catalog data."
        )

        st.code(
            str(exc)
        )

        st.stop()

# ========================================================
    # CATALOG SUMMARY
    # ========================================================

    catalog_count = len(
        catalog_products
    )

    catalog_stock = safe_int(
        catalog_summary_data.get(
            "total_stock",
            sum(
                safe_int(
                    product.get(
                        "stock"
                    )
                )
                for product
                in catalog_products
            ),
        )
    )

    categories = (
        catalog_summary_data.get(
            "categories",
            [],
        )
        or []
    )


    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "Products",
            f"{catalog_count:,}",
        )


    with c2:

        st.metric(
            "Total Stock",
            f"{catalog_stock:,}",
        )


    with c3:

        st.metric(
            "Categories",
            f"{len(categories):,}",
        )


    with c4:

        st.metric(
            "Catalog Storage",
            str(
                catalog_summary_data.get(
                    "storage",
                    "unknown",
                )
            ).upper(),
        )


    st.divider()


    # ========================================================
    # SEARCH
    # ========================================================

    st.markdown(
        "### 🔎 Product Explorer"
    )

    catalog_search = st.text_input(
        "Search catalog",
        placeholder=(
            "backpack / laptop / travel / office..."
        ),
        key="catalog_search_input",
    ).strip()


    filtered_products = (
        catalog_products.copy()
    )


    if catalog_search:

        search_value = (
            catalog_search.lower()
        )

        filtered_products = [

            product

            for product
            in filtered_products

            if search_value
            in " ".join(
                [
                    str(
                        product.get(
                            "product_id",
                            "",
                        )
                    ),
                    str(
                        product.get(
                            "name",
                            "",
                        )
                    ),
                    str(
                        product.get(
                            "category",
                            "",
                        )
                    ),
                    str(
                        product.get(
                            "description",
                            "",
                        )
                    ),
                    " ".join(
                        map(
                            str,
                            product.get(
                                "tags",
                                [],
                            ),
                        )
                    ),
                ]
            ).lower()

        ]


    st.caption(
        f"Showing {len(filtered_products)} "
        f"of {catalog_count} product(s)."
    )


    # ========================================================
    # PRODUCT TABLE
    # ========================================================

    if filtered_products:

        catalog_table = pd.DataFrame(
            [
                {
                    "Product ID":
                        product.get(
                            "product_id"
                        ),

                    "Product":
                        product.get(
                            "name"
                        ),

                    "Category":
                        product.get(
                            "category"
                        ),

                    "Price":
                        format_inr(
                            product.get(
                                "price"
                            )
                        ),

                    "Stock":
                        safe_int(
                            product.get(
                                "stock"
                            )
                        ),

                    "Variants":
                        len(
                            product.get(
                                "variants",
                                [],
                            )
                            or []
                        ),

                    "Tags":
                        ", ".join(
                            map(
                                str,
                                product.get(
                                    "tags",
                                    [],
                                )
                            )
                        ),
                }

                for product
                in filtered_products
            ]
        )


        st.dataframe(
            catalog_table,
            use_container_width=True,
            height=380,
            hide_index=True,
        )

    else:

        st.info(
            "No catalog products match your search."
        )


    st.divider()


    # ========================================================
    # PRODUCT DETAIL / EDITOR
    # ========================================================

    st.markdown(
        "### 🧾 Product Management"
    )


    product_ids = [
        str(
            product.get(
                "product_id"
            )
        )

        for product
        in catalog_products

        if product.get(
            "product_id"
        )
    ]


    editor_mode = st.radio(
        "Action",
        [
            "Add Product",
            "Edit Product",
            "Update Stock",
            "Delete Product",
        ],
        horizontal=True,
        key="catalog_editor_mode",
    )


    # ========================================================
    # ADD PRODUCT
    # ========================================================

    if editor_mode == "Add Product":

        with st.form(
            "catalog_add_product_form",
            clear_on_submit=False,
        ):

            st.markdown(
                "#### ➕ Add New Product"
            )

            a1, a2 = st.columns(2)

            with a1:

                add_product_id = st.text_input(
                    "Product ID",
                    placeholder="M001",
                )

            with a2:

                add_product_name = st.text_input(
                    "Product Name",
                    placeholder="Wireless Mouse Pro",
                )

            add_category = st.text_input(
                "Category",
                placeholder="Computer Accessories",
            )

            a3, a4, a5 = st.columns(3)

            with a3:

                add_price = st.number_input(
                    "Price (₹)",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                )

            with a4:

                add_stock = st.number_input(
                    "Stock",
                    min_value=0,
                    value=0,
                    step=1,
                )

            with a5:

                add_currency = st.text_input(
                    "Currency",
                    value="INR",
                    max_chars=3,
                )

            add_description = st.text_area(
                "Description",
                placeholder="Describe the product...",
            )

            add_features = st.text_input(
                "Features",
                placeholder=(
                    "Wireless, Rechargeable, Ergonomic"
                ),
            )

            add_tags = st.text_input(
                "Tags",
                placeholder=(
                    "mouse, wireless, office"
                ),
            )

            add_related = st.text_input(
                "Related Product IDs",
                placeholder=(
                    "BP001, LS001"
                ),
            )

            add_product_clicked = st.form_submit_button(
                "➕ Create Product",
                use_container_width=True,
                type="primary",
            )


        if add_product_clicked:

            features = [
                value.strip()
                for value
                in add_features.split(",")
                if value.strip()
            ]

            tags = [
                value.strip()
                for value
                in add_tags.split(",")
                if value.strip()
            ]

            related_products = [
                value.strip()
                for value
                in add_related.split(",")
                if value.strip()
            ]


            payload = {
                "product_id":
                    add_product_id.strip(),

                "name":
                    add_product_name.strip(),

                "category":
                    add_category.strip(),

                "price":
                    float(add_price),

                "currency":
                    add_currency.strip().upper(),

                "stock":
                    int(add_stock),

                "description":
                    add_description.strip(),

                "features":
                    features,

                "tags":
                    tags,

                "variants":
                    [],

                "related_products":
                    related_products,
            }


            try:

                response = post_api(
                    "/catalog",
                    payload,
                )

                st.success(
                    "✅ Product created successfully."
                )

                st.json(
                    response
                )

                st.cache_data.clear()

            except Exception as exc:

                st.error(
                    "Unable to create product."
                )

                st.code(
                    str(exc)
                )


    # ========================================================
    # EDIT PRODUCT
    # ========================================================

    elif editor_mode == "Edit Product":

        if not product_ids:

            st.info(
                "No products available to edit."
            )

        else:

            selected_product_id = st.selectbox(
                "Select Product",
                product_ids,
                key="catalog_edit_product_id",
            )


            selected_product = next(

                (
                    product
                    for product
                    in catalog_products
                    if str(
                        product.get(
                            "product_id"
                        )
                    )
                    ==
                    selected_product_id
                ),

                None,
            )


            if selected_product:

                variants = (
                    selected_product.get(
                        "variants",
                        [],
                    )
                    or []
                )


                with st.form(
                    "catalog_edit_product_form",
                    clear_on_submit=False,
                ):

                    st.markdown(
                        "#### ✏️ Edit Product"
                    )

                    e1, e2 = st.columns(2)

                    with e1:

                        edit_name = st.text_input(
                            "Product Name",
                            value=str(
                                selected_product.get(
                                    "name",
                                    "",
                                )
                            ),
                        )

                    with e2:

                        edit_category = st.text_input(
                            "Category",
                            value=str(
                                selected_product.get(
                                    "category",
                                    "",
                                )
                            ),
                        )

                    e3, e4, e5 = st.columns(3)

                    with e3:

                        edit_price = st.number_input(
                            "Price (₹)",
                            min_value=0.0,
                            value=float(
                                selected_product.get(
                                    "price",
                                    0,
                                )
                                or 0
                            ),
                            step=1.0,
                        )

                    with e4:

                        edit_stock = st.number_input(
                            "Stock",
                            min_value=0,
                            value=int(
                                selected_product.get(
                                    "stock",
                                    0,
                                )
                                or 0
                            ),
                            step=1,
                        )

                    with e5:

                        edit_currency = st.text_input(
                            "Currency",
                            value=str(
                                selected_product.get(
                                    "currency",
                                    "INR",
                                )
                            ),
                            max_chars=3,
                        )

                    edit_description = st.text_area(
                        "Description",
                        value=str(
                            selected_product.get(
                                "description",
                                "",
                            )
                        ),
                    )

                    edit_features = st.text_input(
                        "Features",
                        value=", ".join(
                            map(
                                str,
                                selected_product.get(
                                    "features",
                                    [],
                                )
                            )
                        ),
                    )

                    edit_tags = st.text_input(
                        "Tags",
                        value=", ".join(
                            map(
                                str,
                                selected_product.get(
                                    "tags",
                                    [],
                                )
                            )
                        ),
                    )

                    edit_related = st.text_input(
                        "Related Product IDs",
                        value=", ".join(
                            map(
                                str,
                                selected_product.get(
                                    "related_products",
                                    [],
                                )
                            )
                        ),
                    )


                    edit_variants_json = st.text_area(
                        "Variants JSON",
                        value=json.dumps(
                            variants,
                            indent=2,
                        ),
                        height=180,
                    )


                    save_edit = st.form_submit_button(
                        "💾 Save Product",
                        use_container_width=True,
                        type="primary",
                    )


                if save_edit:

                    try:

                        parsed_variants = json.loads(
                            edit_variants_json
                        )

                        if not isinstance(
                            parsed_variants,
                            list,
                        ):

                            raise ValueError(
                                "Variants JSON must be a list."
                            )

                    except Exception as exc:

                        st.error(
                            f"Invalid variants JSON: {exc}"
                        )

                        parsed_variants = None


                    if parsed_variants is not None:

                        payload = {

                            "product_id":
                                selected_product_id,

                            "name":
                                edit_name.strip(),

                            "category":
                                edit_category.strip(),

                            "price":
                                float(edit_price),

                            "currency":
                                edit_currency.strip().upper(),

                            "stock":
                                int(edit_stock),

                            "description":
                                edit_description.strip(),

                            "features": [
                                value.strip()
                                for value
                                in edit_features.split(",")
                                if value.strip()
                            ],

                            "tags": [
                                value.strip()
                                for value
                                in edit_tags.split(",")
                                if value.strip()
                            ],

                            "variants":
                                parsed_variants,

                            "related_products": [
                                value.strip()
                                for value
                                in edit_related.split(",")
                                if value.strip()
                            ],
                        }


                        try:

                            response = put_api(
                                f"/catalog/"
                                f"{selected_product_id}",
                                payload,
                            )

                            st.success(
                                "✅ Product updated successfully."
                            )

                            st.json(
                                response
                            )

                            st.cache_data.clear()

                        except Exception as exc:

                            st.error(
                                "Unable to update product."
                            )

                            st.code(
                                str(exc)
                            )


    # ========================================================
    # UPDATE STOCK
    # ========================================================

    elif editor_mode == "Update Stock":

        if not product_ids:

            st.info(
                "No products available."
            )

        else:

            selected_stock_product = st.selectbox(
                "Select Product",
                product_ids,
                key="catalog_stock_product_id",
            )

            selected_stock_value = st.number_input(
                "New Stock Quantity",
                min_value=0,
                value=int(
                    next(
                        (
                            product.get(
                                "stock",
                                0,
                            )
                            for product
                            in catalog_products
                            if str(
                                product.get(
                                    "product_id"
                                )
                            )
                            ==
                            selected_stock_product
                        ),
                        0,
                    )
                    or 0
                ),
                step=1,
            )


            if st.button(
                "📦 Update Stock",
                use_container_width=True,
                type="primary",
                key="catalog_update_stock_button",
            ):

                try:

                    response = patch_api(
                        f"/catalog/"
                        f"{selected_stock_product}"
                        "/stock",
                        {
                            "stock":
                                int(
                                    selected_stock_value
                                )
                        },
                    )

                    st.success(
                        "✅ Stock updated successfully."
                    )

                    st.json(
                        response
                    )

                    st.cache_data.clear()

                except Exception as exc:

                    st.error(
                        "Unable to update stock."
                    )

                    st.code(
                        str(exc)
                    )


    # ========================================================
    # DELETE PRODUCT
    # ========================================================

    else:

        if not product_ids:

            st.info(
                "No products available."
            )

        else:

            delete_product_id = st.selectbox(
                "Select Product to Delete",
                product_ids,
                key="catalog_delete_product_id",
            )


            st.warning(
                "Deleting a catalog product is permanent "
                "for the active storage backend."
            )


            confirm_delete = st.checkbox(
                "I understand that this product will be deleted.",
                key="catalog_confirm_delete",
            )


            if st.button(
                "🗑️ Delete Product",
                use_container_width=True,
                type="primary",
                disabled=not confirm_delete,
                key="catalog_delete_button",
            ):

                try:

                    response = delete_api(
                        f"/catalog/"
                        f"{delete_product_id}"
                    )

                    st.success(
                        "✅ Product deleted successfully."
                    )

                    st.json(
                        response
                    )

                    st.cache_data.clear()

                except Exception as exc:

                    st.error(
                        "Unable to delete product."
                    )

                    st.code(
                        str(exc)
                    )


# ============================================================
#  TAB 4 — BUYER AI\# 
# ============================================================

with tabs[3]:

    # ========================================================
    # BUYER AI
    # ========================================================

    st.markdown(
        '<div class="section-title">'
        "🤖 MerchantOps Buyer AI"
        "</div>",
        unsafe_allow_html=True,
    )

    st.caption(
        "A conversational shopping assistant powered by your "
        "live merchant catalog."
    )

    # ========================================================
    # SHOPPING SESSION
    # ========================================================

    if st.session_state.get("buyer_cart_id"):

        st.caption(
            "🛒 Shopping session active"
        )

    else:

        st.caption(
            "🛒 A shopping cart will be created automatically."
        )

    # ========================================================
    # QUICK PROMPTS
    # ========================================================

    st.markdown(
        "### 💡 Try a shopping request"
    )

    qp1, qp2, qp3, qp4 = st.columns(4)

    with qp1:

        if st.button(
            "🎒 Backpack under ₹2,000",
            use_container_width=True,
            key="buyer_quick_backpack",
        ):

            st.session_state[
                "buyer_pending_prompt"
            ] = (
                "I need a laptop backpack under ₹2000 "
                "for office and travel"
            )

    with qp2:

        if st.button(
            "💻 Laptop accessories",
            use_container_width=True,
            key="buyer_quick_laptop",
        ):

            st.session_state[
                "buyer_pending_prompt"
            ] = (
                "Show me laptop accessories"
            )

    with qp3:

        if st.button(
            "✈️ Travel products",
            use_container_width=True,
            key="buyer_quick_travel",
        ):

            st.session_state[
                "buyer_pending_prompt"
            ] = (
                "Show me products for travel"
            )

    with qp4:

        if st.button(
            "🔥 Best value",
            use_container_width=True,
            key="buyer_quick_value",
        ):

            st.session_state[
                "buyer_pending_prompt"
            ] = (
                "What is the best value product "
                "available right now?"
            )

    st.divider()

    # ========================================================
    # CHAT HISTORY
    # ========================================================

    for message in st.session_state.get(
        "buyer_messages",
        [],
    ):

        role = message.get(
            "role",
            "assistant",
        )

        if role not in {
            "user",
            "assistant",
        }:

            role = "assistant"

        content = str(
            message.get(
                "content",
                "",
            )
        )

        with st.chat_message(
            role
        ):

            st.markdown(
                content
            )

    # ========================================================
    # INPUT
    # ========================================================

    pending_prompt = st.session_state.pop(
        "buyer_pending_prompt",
        "",
    )

    user_message = st.text_input(
        "Ask me what you want to buy",
        placeholder=(
            "Example: Show me laptop backpacks"
        ),
        key="buyer_text_input",
    )

    send_button = st.button(
        "🤖 Send to Buyer AI",
        use_container_width=True,
        type="primary",
        key="buyer_send_message",
    )

    # A quick prompt automatically becomes the message.
    if pending_prompt:

        user_message = pending_prompt
        send_button = True

    # ========================================================
    # PROCESS MESSAGE
    # ========================================================

    if send_button:

        user_message = str(
            user_message
        ).strip()

        if not user_message:

            st.warning(
                "Please enter a shopping request."
            )

        else:

            st.session_state[
                "buyer_messages"
            ].append(
                {
                    "role": "user",
                    "content": user_message,
                }
            )

            try:

                # ------------------------------------------------
                # CREATE CART
                # ------------------------------------------------

                if not st.session_state.get(
                    "buyer_cart_id"
                ):

                    st.session_state[
                        "buyer_cart_id"
                    ] = create_buyer_cart()

                # ------------------------------------------------
                # BUYER AI REQUEST
                # ------------------------------------------------

                with st.spinner(
                    "🤖 Buyer AI is thinking..."
                ):

                    buyer_response = post_api(
                        "/buyer/chat",
                        {
                            "message":
                                user_message,

                            "session_id":
                                st.session_state[
                                    "buyer_session_id"
                                ],

                            "cart_id":
                                st.session_state[
                                    "buyer_cart_id"
                                ],
                        },
                    )

                # ------------------------------------------------
                # CART ID
                # ------------------------------------------------

                returned_cart_id = (
                    buyer_response.get(
                        "cart_id"
                    )
                )

                if returned_cart_id:

                    st.session_state[
                        "buyer_cart_id"
                    ] = str(
                        returned_cart_id
                    )

                # ------------------------------------------------
                # CART
                # ------------------------------------------------

                returned_cart = (
                    buyer_response.get(
                        "cart"
                    )
                )

                if returned_cart is not None:

                    st.session_state[
                        "buyer_current_cart"
                    ] = returned_cart

                # ------------------------------------------------
                # RESPONSE
                # ------------------------------------------------

                intent = buyer_response.get(
                    "intent",
                    "UNKNOWN",
                )

                response_text = str(
                    buyer_response.get(
                        "message",
                        (
                            "I couldn't find a suitable "
                            "product right now."
                        ),
                    )
                )

                products = (
                    buyer_response.get(
                        "products",
                        [],
                    )
                    or []
                )
                
                st.session_state[
                    "buyer_products"
                ] = products

                filters = (
                    buyer_response.get(
                        "filters",
                        {},
                    )
                    or {}
                )

                st.session_state[
                    "buyer_last_response"
                ] = buyer_response

                st.session_state[
                    "buyer_messages"
                ].append(
                    {
                        "role":
                            "assistant",

                        "content":
                            response_text,
                    }
                )

                # ------------------------------------------------
                # RESPONSE DISPLAY
                # ------------------------------------------------

                st.markdown(
                    "### 🤖 Buyer AI Response"
                )

                st.success(
                    response_text
                )

                r1, r2 = st.columns(2)

                with r1:

                    st.metric(
                        "Detected Intent",
                        str(intent),
                    )

                with r2:

                    st.metric(
                        "Matches",
                        len(products),
                    )

                # ------------------------------------------------
                # FILTERS
                # ------------------------------------------------

                if filters:

                    st.markdown(
                        "#### 🎯 Understood Requirements"
                    )

                    rows = []

                    for key, value in (
                        filters.items()
                    ):

                        if isinstance(
                            value,
                            list,
                        ):

                            value = ", ".join(
                                map(
                                    str,
                                    value,
                                )
                            )

                        rows.append(
                            {
                                "Requirement":
                                    str(key),

                                "Value":
                                    str(value),
                            }
                        )

                    if rows:

                        st.dataframe(
                            pd.DataFrame(
                                rows
                            ),
                            use_container_width=True,
                            hide_index=True,
                        )

                # ------------------------------------------------
                # PRODUCTS
                # ------------------------------------------------

               

                    if (
                                        not products
                                        and
                                        intent == "PRODUCT_SEARCH"
                                        ):

                                        st.warning(
                                            "No matching in-stock products "
                                            "were returned by Buyer AI."
                                            )

                                        st.warning(
                                            "No matching in-stock products "
                                            "were returned by Buyer AI."
                                        )
                                        
            except Exception as exc:

                                        st.error(
                                            "Unable to reach Buyer AI."
                                        )

                                        st.code(
                                            str(exc)
                                        )
                                        
                                        
# ========================================================
# PERSISTED RECOMMENDED PRODUCTS
# ========================================================

saved_products = (
    st.session_state.get(
        "buyer_products",
        [],
    )
    or []
)

if saved_products:

    st.markdown(
        "### 🛍️ Recommended Products"
    )

    for index, product in enumerate(
        saved_products[:5]
    ):

        product_id = str(
            product.get(
                "product_id",
                "",
            )
        )

        product_name = str(
            product.get(
                "name",
                "Product",
            )
        )

        price = safe_float(
            product.get(
                "price",
                0,
            )
        )

        stock = safe_int(
            product.get(
                "stock",
                0,
            )
        )

        category = str(
            product.get(
                "category",
                "",
            )
        )

        description = str(
            product.get(
                "description",
                "",
            )
        )

        with st.container(
            border=True
        ):

            # ====================================================
            # PRODUCT INFORMATION
            # ====================================================

            p1, p2, p3 = st.columns(
                [3, 1, 1]
            )

            with p1:

                st.markdown(
                    f"#### {product_name}"
                )

                st.caption(
                    f"{product_id} • {category}"
                )

            with p2:

                st.metric(
                    "Price",
                    format_inr(
                        price
                    ),
                )

            with p3:

                st.metric(
                    "Stock",
                    stock,
                )

            if description:

                st.write(
                    description
                )

            features = (
                product.get(
                    "features",
                    [],
                )
                or []
            )

            if features:

                st.caption(
                    " • ".join(
                        map(
                            str,
                            features[:4],
                        )
                    )
                )

            # ====================================================
            # ACTION BUTTONS
            # ====================================================

            a1, a2 = st.columns(2)

            # ----------------------------------------------------
            # VIEW DETAILS
            # ----------------------------------------------------

            with a1:

                if st.button(
                    "🔍 View Details",
                    use_container_width=True,
                    key=(
                        "buyer_saved_details_"
                        f"{product_id}_"
                        f"{index}"
                    ),
                ):

                    try:

                        detail_response = post_api(
                            "/buyer/chat",
                            {
                                "message":
                                    (
                                        "Tell me more about "
                                        f"{product_name}"
                                    ),

                                "session_id":
                                    st.session_state[
                                        "buyer_session_id"
                                    ],

                                "cart_id":
                                    st.session_state[
                                        "buyer_cart_id"
                                    ],
                            },
                        )

                        detail_text = str(
                            detail_response.get(
                                "message",
                                "No additional details available.",
                            )
                        )

                        detail_cart = (
                            detail_response.get(
                                "cart"
                            )
                        )

                        if detail_cart is not None:

                            st.session_state[
                                "buyer_current_cart"
                            ] = detail_cart

                        st.info(
                            detail_text
                        )

                    except Exception as exc:

                        st.error(
                            "Unable to load product details."
                        )

                        st.code(
                            str(exc)
                        )

            # ----------------------------------------------------
            # ADD TO CART
            # ----------------------------------------------------

            with a2:

                if st.button(
                    "➕ Add to Cart",
                    use_container_width=True,
                    type="primary",
                    key=(
                        "buyer_saved_add_"
                        f"{product_id}_"
                        f"{index}"
                    ),
                ):

                    try:

                        # ------------------------------------------------
                        # Send add-to-cart request
                        # ------------------------------------------------

                        add_response = post_api(
    "/buyer/chat",
    {
        "message":
            f"Add {product_id}",

        "session_id":
            st.session_state[
                "buyer_session_id"
            ],

        "cart_id":
            st.session_state[
                "buyer_cart_id"
            ],
    },
)

                        # ------------------------------------------------
                        # Update cart ID
                        # ------------------------------------------------

                        returned_cart_id = (
                            add_response.get(
                                "cart_id"
                            )
                        )

                        if returned_cart_id:

                            st.session_state[
                                "buyer_cart_id"
                            ] = str(
                                returned_cart_id
                            )

                        # ------------------------------------------------
                        # Update cart from Buyer AI response
                        # ------------------------------------------------

                        returned_cart = (
                            add_response.get(
                                "cart"
                            )
                        )

                        if returned_cart is not None:

                            st.session_state[
                                "buyer_current_cart"
                            ] = returned_cart

                        # ------------------------------------------------
                        # Fallback: fetch authoritative cart
                        # ------------------------------------------------

                        else:

                            active_cart_id = (
                                st.session_state.get(
                                    "buyer_cart_id"
                                )
                            )

                            if active_cart_id:

                                try:

                                    cart_response = fetch_cart_direct(
    str(active_cart_id)
)

                                    api_cart = (
                                        cart_response.get(
                                            "cart"
                                        )
                                    )

                                    if isinstance(
                                        api_cart,
                                        dict,
                                    ):

                                        st.session_state[
                                            "buyer_current_cart"
                                        ] = api_cart

                                except Exception:

                                    pass

                        # ------------------------------------------------
                        # Success message
                        # ------------------------------------------------

                        add_text = str(
                            add_response.get(
                                "message",
                                (
                                    f"{product_name} "
                                    "added to your cart."
                                ),
                            )
                        )

                        st.session_state[
                            "buyer_messages"
                        ].append(
                            {
                                "role":
                                    "assistant",

                                "content":
                                    add_text,
                            }
                        )

                        st.success(
                            add_text
                        )

                        # ------------------------------------------------
                        # Refresh the complete Buyer AI tab
                        # ------------------------------------------------

                        st.rerun()

                    except Exception as exc:

                        st.error(
                            "Unable to add product to cart."
                        )

                        st.code(
                            str(exc)
                        )
    # ========================================================
    # CURRENT CART
    # ========================================================

    current_cart = (
        st.session_state.get(
            "buyer_current_cart"
        )
        or {}
    )

    # Refresh from backend whenever a cart ID exists.
    active_cart_id = (
        st.session_state.get(
            "buyer_cart_id"
        )
    )

    if active_cart_id:

        try:

            cart_response = fetch_cart_direct(
    str(active_cart_id)
)

            api_cart = (
                cart_response.get(
                    "cart"
                )
            )

            if isinstance(
                api_cart,
                dict,
            ):

                current_cart = api_cart

                st.session_state[
                    "buyer_current_cart"
                ] = api_cart

        except Exception:

            pass

    st.divider()

    st.markdown(
        "### 🛒 Your Cart"
    )

    items = (
        current_cart.get(
            "items",
            [],
        )
        or []
    )

    if items:

        for item_index, item in enumerate(items):

            quantity = safe_int(
                item.get(
                    "quantity",
                    0,
                )
            )

            item_name = str(
                item.get(
                    "product_name",
                    "Product",
                )
            )

            product_id = str(
                item.get(
                    "product_id",
                    "",
                )
            )

            variant_id = item.get(
                "variant_id"
            )

            label = (
                f"{quantity} × {item_name}"
            )

            if item.get("variant_name"):

                label += (
                    f" ({item.get('variant_name')})"
                )

            cart_col1, cart_col2 = st.columns(
                [5, 1]
            )

            with cart_col1:

                st.write(
                    f"**{label}** — "
                    f"{format_inr(item.get('line_total', 0))}"
                )

            with cart_col2:

                with cart_col2:

                    if st.button(
                        "🗑️ Remove",
                        use_container_width=True,
                        key=(
                            "buyer_remove_cart_"
                            f"{product_id}_"
                            f"{variant_id}_"
                            f"{item_index}"
                        ),
                    ):

                        try:

                            active_cart_id = (
                                st.session_state.get(
                                    "buyer_cart_id"
                                )
                            )

                            if not active_cart_id:

                                st.error(
                                    "No active shopping cart found."
                                )

                            else:

                                remove_response = post_api(
                                    "/buyer/chat",
                                    {
                                        "message":
                                            f"Remove {product_id}",

                                        "session_id":
                                            st.session_state[
                                                "buyer_session_id"
                                            ],

                                        "cart_id":
                                            active_cart_id,
                                    },
                                )

                                returned_cart_id = (
                                    remove_response.get(
                                        "cart_id"
                                    )
                                )

                                if returned_cart_id:

                                    st.session_state[
                                        "buyer_cart_id"
                                    ] = str(
                                        returned_cart_id
                                    )

                                updated_cart = (
                                    remove_response.get(
                                        "cart"
                                    )
                                )

                                if updated_cart is not None:

                                    st.session_state[
                                        "buyer_current_cart"
                                    ] = updated_cart

                                if remove_response.get(
                                    "success",
                                    False,
                                ):

                                    st.success(
                                        remove_response.get(
                                            "message",
                                            f"{item_name} removed from your cart.",
                                        )
                                    )

                                else:

                                    st.error(
                                        remove_response.get(
                                            "message",
                                            f"Unable to remove {item_name}.",
                                        )
                                    )

                                st.rerun()

                        except Exception as exc:

                            st.error(
                                "Unable to remove item from cart."
                            )

                            st.code(
                                str(exc)
                            )
        # ====================================================
        # CHECKOUT
        # ====================================================

        st.markdown(
            "### 💳 Checkout"
        )

        checkout_api_mode = (
            "production"
            if "onrender.com" in API_URL
            else "local"
        )

        checkout_url = (
            f"{CHECKOUT_URL}"
            f"?cart_id="
            f"{st.session_state.get('buyer_cart_id', '')}"
            f"&api="
            f"{checkout_api_mode}"
        )

        st.link_button(
            "💳 Proceed to Checkout",
            checkout_url,
            use_container_width=True,
        )

    else:

        st.info(
            "Your cart is empty. Add a product above to begin checkout."
        )

    # ========================================================
    # NEW SHOPPING SESSION
    # ========================================================

    st.divider()

    if st.button(
        "🆕 Start New Shopping Session",
        use_container_width=True,
        key="buyer_new_session",
    ):

        st.session_state[
            "buyer_session_id"
        ] = (
            f"buyer_{uuid.uuid4().hex[:12]}"
        )

        st.session_state[
            "buyer_cart_id"
        ] = None

        st.session_state[
            "buyer_messages"
        ] = []

        st.session_state[
            "buyer_current_cart"
        ] = None

        st.session_state[
            "buyer_last_response"
        ] = None

        st.session_state[
            "buyer_selected_product"
        ] = None

        st.rerun()


# ============================================================
# TAB 4 — PAYMENTS
# ============================================================
with tabs[4]:

    try:

        payments_data = get_payments_data(
            payment_source
        )

        verified_data = get_verified_data()

        merchant_orders_data = (
            get_merchant_orders_data()
        )

        activity_data = get_activity_data()

        webhook_data = get_webhook_data()

        verified_payments = (
            verified_data.get(
                "payments",
                [],
            )
            or []
        )

        merchant_orders = (
            merchant_orders_data.get(
                "orders",
                [],
            )
            or []
        )

        webhook_events = (
            webhook_data.get(
                "events",
                [],
            )
            or []
        )

    except Exception as exc:

        st.error(
            "❌ Unable to load Payments data."
        )

        st.code(
            str(exc)
        )

        st.stop()

    # YOUR EXISTING PAYMENTS UI CONTINUES HERE

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
# TAB 5 — AI RECOVERY
# ============================================================

with tabs[5]:

    try:

        analysis_data = get_analysis_data(
            payment_source
        )

        decisions_data = get_decisions_data(
            payment_source
        )

        decision_records = (
            decisions_data.get(
                "decisions",
                [],
            )
            or []
        )

    except Exception as exc:

        st.error(
            "❌ Unable to load AI Recovery data."
        )

        st.code(
            str(exc)
        )

        st.stop()

    # YOUR EXISTING AI RECOVERY UI CONTINUES HERE

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
# TAB 6 — APPROVALS
# ============================================================

with tabs[6]:

    try:

        decisions_data = get_decisions_data(
            payment_source
        )

        decision_records = (
            decisions_data.get(
                "decisions",
                [],
            )
            or []
        )

    except Exception as exc:

        st.error(
            "❌ Unable to load Approval data."
        )

        st.code(
            str(exc)
        )

        st.stop()

    # YOUR EXISTING APPROVAL UI CONTINUES HERE


# ============================================================
# TAB 7 — WEBHOOKS
# ============================================================

with tabs[7]:

    try:

        webhook_data = get_webhook_data()

        webhook_events = (
            webhook_data.get(
                "events",
                [],
            )
            or []
        )

    except Exception as exc:

        st.error(
            "❌ Unable to load Webhook data."
        )

        st.code(
            str(exc)
        )

        st.stop()

    # YOUR EXISTING WEBHOOK UI CONTINUES HERE


# ============================================================
# TAB 8 — AUDIT
# ============================================================

with tabs[8]:

    try:

        audit_data = get_audit_data()

        audit_events = (
            audit_data.get(
                "events",
                [],
            )
            or []
        )

    except Exception as exc:

        st.error(
            "❌ Unable to load Audit data."
        )

        st.code(
            str(exc)
        )

        st.stop()

    # YOUR EXISTING AUDIT UI CONTINUES HERE


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

st.markdown(
    '<div id="mo-bottom"></div>',
    unsafe_allow_html=True,
)
