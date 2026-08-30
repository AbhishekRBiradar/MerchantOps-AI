# 💳 MerchantOps AI

## Agentic Payment Intelligence, Revenue Recovery & Governed Decision Automation

MerchantOps AI is an AI-powered merchant operations platform designed to analyze payment failures, estimate revenue recovery opportunities, assess transaction risk, simulate recovery strategies, generate explainable decisions, and enforce governance controls.

The platform combines **AI/ML decision agents, FastAPI, PostgreSQL, Razorpay Test Mode, webhook processing, audit logging, and Streamlit** into an end-to-end merchant intelligence system.

---

## 🚀 Project Overview

Failed payments can create significant revenue leakage for merchants.

MerchantOps AI analyzes failed transactions and determines the most appropriate recovery strategy using:

- Revenue opportunity analysis
- Transaction risk scoring
- Recovery probability
- Recovery simulation
- Expected recovery estimation
- Decision confidence
- Governance policies
- Merchant approval requirements

Possible recovery actions include:

RETRY_NOW
RETRY_LATER
REVIEW
DO_NOTHING


🔑 Key Features

1. Payment Intelligence
Payment performance analysis
Failed payment identification
Success/failure rate calculation
Revenue-at-risk calculation
Captured payment analysis
Razorpay payment verification


2. Agentic AI Pipeline
MerchantOps AI uses multiple specialized stages:

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
Final Decision

The system generates:

Risk score
Risk level
Recovery probability
Expected recovery
Simulation scenarios
Decision confidence
Final action
Decision explanation


3. Revenue Recovery
For failed payments, the platform estimates the potential recovery value.

Example:

Payment Amount              ₹9,875
Risk Score                    0.42
Risk Level                    MEDIUM
Recovery Probability         38.8%
Expected Recovery          ₹3,829
Final Decision        RETRY_LATER

4. Governance & Safety
AI recommendations are passed through governance controls before an action can be considered for execution.

The system supports:
MERCHANT_APPROVAL
SCHEDULED_TEST_ACTION
BLOCKED
NO_ACTION

Governance mechanisms include:
Merchant approval requirements
High-risk action blocking
Scheduled test actions
Action policy evaluation
Execution-mode classification
Audit logging

Example:
High Risk Transaction
        ↓
Risk Assessment
        ↓
DO_NOTHING
        ↓
BLOCKED


💳 Razorpay Integration
MerchantOps AI integrates with Razorpay Test Mode.

Implemented functionality includes:

Razorpay order creation
Razorpay Checkout integration
Payment signature verification
HMAC-SHA256 verification
Trusted payment retrieval
Verified payment persistence
Payment status validation
Razorpay webhook processing
Payment Verification Flow

Razorpay Checkout
       ↓
Create Order
       ↓
Payment
       ↓
Checkout Response
       ↓
HMAC-SHA256 Signature Verification
       ↓
Fetch Trusted Payment Data
       ↓
Persist Verification Event
       ↓
PostgreSQL
       ↓
Verified Payment API

Verified payments are exposed through:

GET /payments/verified

Example verified payment information includes:

Payment ID
Order ID
Amount
Currency
Payment Status
Payment Method
Captured Status
Refund Amount
Email
Contact


🔔 Razorpay Webhooks
Webhook endpoint:

POST /webhooks/razorpay

The webhook pipeline performs:

Razorpay Webhook
       ↓
Signature Verification
       ↓
x-razorpay-event-id
       ↓
Duplicate Detection
       ↓
PostgreSQL Idempotency
       ↓
Webhook Processing
       ↓
MerchantOps AI
       ↓
Audit Trail


Supported payment lifecycle events include:

payment.authorized
payment.captured
payment.failed

Webhook events are available through:

GET /webhooks/events
🔐 Webhook Idempotency

Webhook event processing uses:

x-razorpay-event-id

as the idempotency key.

The event ID is stored in PostgreSQL with a uniqueness constraint.


Conceptually:

Webhook Event
      ↓
Event ID
      ↓
Already Exists?
   ↙       ↘
 YES       NO
 ↓          ↓
Ignore     Process
            ↓
         Persist

This prevents duplicate webhook events from being processed repeatedly.


🗄️ PostgreSQL Persistence
Production persistence uses PostgreSQL.

Main tables:

audit_logs
webhook_events
Audit Logs

The audit_logs table stores:

Timestamp
Event type
Payment ID
Decision
Action
Risk level
Approval requirement
Execution mode
Status
Structured details

Audit details are stored using PostgreSQL JSONB.
Webhook Events

The webhook_events table stores:

Event ID
Event name
Payment ID
Creation timestamp

The event ID is used to enforce webhook idempotency.


📊 Production Activity Statistics
The backend exposes aggregate activity statistics through:

GET /activity/stats

Example:

{
  "storage": "postgresql",
  "verified_payments": 1,
  "verification_events": 3,
  "webhook_events": 14,
  "webhook_processing": 16
}

These values are calculated directly from PostgreSQL rather than from a limited audit-result subset.


🤖 AI Decision Engine
The final decision layer evaluates:

Risk
Recovery Opportunity
Simulation Results
Confidence
Governance Policy

and produces a final action:

RETRY_NOW
RETRY_LATER
REVIEW
DO_NOTHING

Example:

Risk Score              0.42
Risk Level              MEDIUM
Recovery Probability    38.8%
Expected Recovery       ₹3,829
Decision                RETRY_LATER
Confidence              58%
Execution Mode          SCHEDULED_TEST_ACTION


🛡️ Action Guardrails
The action policy layer controls whether a recommended action can proceed.

Examples:

High-risk transaction
Risk Level: HIGH
Recommendation: DO_NOTHING

Policy Result:
BLOCKED
Strong recovery opportunity
Recommendation:
RETRY_NOW

Policy Result:
MERCHANT_APPROVAL
Controlled delayed retry
Recommendation:
RETRY_LATER

Policy Result:
SCHEDULED_TEST_ACTION

This provides an additional safety layer around AI-generated recommendations.


🖥️ Streamlit Dashboard
MerchantOps AI includes an interactive Streamlit dashboard connected to the production FastAPI backend.


Dashboard Sections
📊 Merchant Operations Overview
Displays:

Total payments
Failed payments
Success rate
Failure rate
Revenue at risk

💳 Razorpay Live Activity
Displays:

Verified payments
Verification events
Webhook events
Webhook processing

🔔 Razorpay Webhook Activity
Displays stored Razorpay webhook events.

🤖 AI Executive Summary
Displays:

Revenue at risk
Recovery candidates
Expected recovery
AI decisions

🎯 AI Action Recommendations
Displays:

RETRY_NOW
RETRY_LATER
REVIEW
DO_NOTHING

🛡️ AI Governance & Safety
Displays:

Merchant approvals
Allowed actions
Blocked actions
Scheduled test actions

🔎 Decision Explorer
Allows decisions to be explored using:

Action filter
Risk filter
Row limit

⏳ Merchant Approval Queue
Displays decisions that require merchant approval.

🧠 Decision Details & Explainability
Displays:

Payment ID
Order ID
Customer
Amount
Payment method
Failure reason
Risk score
Expected recovery
Confidence
Final decision
Decision reason
Policy mode

🧪 Simulation Analysis
Displays simulated recovery scenarios and expected recovery values.

✅ Verified Payment Details

Displays successfully verified Razorpay payments.

📋 Audit Trail

Displays recorded operational events from the backend.


🏗️ System Architecture
                       ┌─────────────────────┐
                       │   Razorpay Checkout │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Create Razorpay   │
                       │       Order         │
                       └──────────┬──────────┘
                                  │
                                  ▼
                              Payment
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Payment Signature   │
                       │    Verification     │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Payment Provider /  │
                       │      Adapter        │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │    Revenue Agent    │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │      Risk Agent     │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │  Simulation Agent   │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   Decision Agent    │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │  Action Guardrails  │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │     PostgreSQL      │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │   MerchantOps API   │
                       │       FastAPI       │
                       └──────────┬──────────┘
                                  │
                                  ▼
                       ┌─────────────────────┐
                       │ Streamlit Dashboard │
                       └─────────────────────┘


🔄 Webhook Architecture

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
Audit Trail


📈 Demonstration Results
The current demonstration dataset contains:

Total Payments        1,000
Failed Payments         103
Captured Payments       897
Failure Rate           10.3%
Revenue at Risk      ₹582,795

AI analysis:

Recovery Candidates      103
Risk Candidates          103
Simulation Candidates   103
AI Decisions             103

Decision distribution:

RETRY_NOW                 3
RETRY_LATER              23
REVIEW                    8
DO_NOTHING               69

Governance:

Merchant Approval        11
Allowed Actions          34
Blocked Actions          69
Scheduled Test Actions   23

These values represent the current demonstration dataset and are not live financial statistics.


🌐 REST API
System
GET /
GET /health
GET /health/database
GET /activity/stats
Payments
GET /payments
GET /payments/verified
POST /razorpay/create-order
POST /razorpay/verify-payment
AI
GET /analyze
GET /decisions
Audit
GET /audit
Webhooks
GET /webhooks/events
POST /webhooks/razorpay


🧪 Testing
The project includes automated tests covering:

Action Tools
Audit Logging
Decision Agent
Orchestrator
Payment Adapter
Payment Provider
Payment Verification
Revenue Agent
Risk Agent
Simulation Agent
Razorpay Webhook Handling
Webhook Event Persistence
Webhook Processing

Current test result:

27 passed

Run the complete test suite:

python -m pytest

☁️ Deployment
Backend

The FastAPI backend is deployed using:

Render

Production API:
https://merchantops-ai-api.onrender.com

Dashboard
The Streamlit dashboard communicates with the production API.

Streamlit Dashboard
        ↓
FastAPI API
        ↓
PostgreSQL

⚙️ Technology Stack
Backend
Python
FastAPI
REST APIs
AI / Data
Pandas
Risk Scoring
Recovery Simulation
Decision Automation
Agentic AI Workflow
Database
PostgreSQL
JSONB
Payment Integration
Razorpay API
Razorpay Checkout
Razorpay Webhooks
HMAC-SHA256
Frontend
Streamlit
Testing
Pytest
Deployment & Version Control
Render
Streamlit
Git
GitHub


📁 Project Structure
MerchantOps-AI/
│
├── backend/
│   ├── agents/
│   │   ├── revenue_agent.py
│   │   ├── risk_agent.py
│   │   ├── simulation_agent.py
│   │   ├── decision_agent.py
│   │   └── orchestrator.py
│   │
│   ├── database/
│   │   ├── postgres.py
│   │   ├── audit.py
│   │   └── webhook_events.py
│   │
│   ├── tools/
│   │   ├── payment_provider.py
│   │   └── webhook_processor.py
│   │
│   └── main.py
│
├── dashboard/
│   └── app.py
│
├── razorpay/
│   ├── client.py
│   ├── webhook.py
│   └── checkout.html
│
├── tests/
│   ├── test_action_tools.py
│   ├── test_audit.py
│   ├── test_decision_agent.py
│   ├── test_orchestrator.py
│   ├── test_payment_adapter.py
│   ├── test_payment_provider.py
│   ├── test_payment_verification.py
│   ├── test_revenue_agent.py
│   ├── test_risk_agent.py
│   ├── test_simulation_agent.py
│   ├── test_webhook.py
│   ├── test_webhook_events.py
│   └── test_webhook_processor.py
│
├── data/
├── requirements.txt
└── README.md


🚀 Local Setup

1. Clone the Repository
git clone https://github.com/AbhishekRBiradar/MerchantOps-AI.git
cd MerchantOps-AI

2. Create Virtual Environment
python -m venv .venv
Windows
.venv\Scripts\activate

3. Install Dependencies
pip install -r requirements.txt

4. Configure Environment Variables

Create a .env file:

DATABASE_URL=your_postgresql_connection_string

RAZORPAY_KEY_ID=your_razorpay_test_key_id
RAZORPAY_KEY_SECRET=your_razorpay_test_key_secret
RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret

Never commit .env to GitHub.

5. Start FastAPI
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

6. Start Streamlit
set API_URL=https://merchantops-ai-api.onrender.com
streamlit run dashboard/app.py

7. Run Tests
python -m pytest


🔐 Security
Sensitive credentials are provided through environment variables rather than hard-coded into application source code.

Required configuration:

DATABASE_URL
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET

Security mechanisms include:

HMAC-SHA256 payment signature verification
Razorpay webhook signature verification
Webhook event idempotency
PostgreSQL persistence
Audit logging
Governance guardrails
Merchant approval controls

Sensitive credentials must never be committed to the repository.

⚠️ Limitations
Razorpay integration currently runs in Test Mode.
AI recovery decisions are intended for demonstration, research, and controlled automation.
Scheduled actions are governed test actions.
The system is not an unrestricted live-money payment execution engine.
Production financial, fraud, risk, and compliance decisions would require additional validation, monitoring, controls, and regulatory considerations.


📌 Project Status
FastAPI Backend                 ✅
Payment Intelligence            ✅
Revenue Analysis                ✅
Risk Analysis                   ✅
Recovery Simulation             ✅
AI Decision Automation          ✅
Governance & Guardrails         ✅
Razorpay Test Mode              ✅
Payment Verification            ✅
Webhook Processing              ✅
Webhook Idempotency             ✅
PostgreSQL Persistence          ✅
Audit Logging                   ✅
Activity Statistics             ✅
Streamlit Dashboard             ✅
Render Deployment               ✅
Automated Tests                 ✅


⭐ Project Highlights
Agentic AI
Payment Intelligence
Revenue Recovery
Risk Scoring
Recovery Simulation
Explainable Decisions
Governance
Merchant Approval
Razorpay Integration
Webhook Idempotency
PostgreSQL
FastAPI
Streamlit
Production Deployment
Automated Testing


👨‍💻 Author
Abhishek Rajkumar Biradar
AI/ML | Python | Backend Development | Data & AI Systems

GitHub:
https://github.com/AbhishekRBiradar


📄 Disclaimer

MerchantOps AI is a portfolio and academic engineering project demonstrating payment intelligence, AI-assisted decisioning, governance, payment integration, webhook processing, and production-style backend architecture using Razorpay Test Mode.

It is not intended to replace production financial risk, fraud detection, payment authorization, compliance, or regulatory systems.
