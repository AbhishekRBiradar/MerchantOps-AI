# 💳 MerchantOps AI

## Agentic Commerce, Payment Intelligence, Revenue Recovery & Governed Decision Automation

MerchantOps AI is an AI-powered merchant operations and agentic commerce platform designed to connect the customer buying journey with intelligent merchant-side payment decisioning.

The platform combines:

- 🤖 AI-powered Buyer Assistant
- 🛍️ Conversational product discovery
- 🎯 AI product recommendations
- 🛒 Intelligent cart management
- 💳 Razorpay checkout and payment processing
- ✅ Payment verification
- 📈 Revenue recovery analysis
- ⚠️ Transaction risk assessment
- 🧪 Recovery simulation
- 🧠 Explainable AI decisions
- 🛡️ Governance and safety controls
- 🔔 Razorpay webhook processing
- 🗄️ PostgreSQL persistence
- 📋 Audit logging
- 📊 Streamlit merchant dashboard

The project demonstrates how AI agents can support both sides of commerce:

**Customer → Product Discovery → Cart → Checkout → Payment → Verification → Merchant Intelligence**

---

# 🚀 Project Overview

Traditional online commerce usually requires customers to manually search for products, compare options, select products, manage quantities, navigate through checkout, and complete payment.

At the same time, merchants need to monitor payment performance, understand failed transactions, identify revenue at risk, evaluate transaction risk, estimate recovery opportunities, and determine appropriate actions.

MerchantOps AI brings these workflows together into one platform.

A customer can communicate with an AI shopping assistant using natural language.

For example:

```text
Customer:
Show me backpacks

Buyer AI:
Finds and recommends relevant products

Customer:
Add Laptop Backpack Pro

Buyer AI:
Adds the product to the shopping cart

Customer:
Show my cart

Buyer AI:
Displays the cart, quantities and total

Customer:
Checkout

System:
Creates a Razorpay payment order

Customer:
Completes payment

System:
Verifies the Razorpay payment
```

After the customer completes the payment journey, MerchantOps AI also provides merchant-side intelligence for analysing payment failures, revenue recovery opportunities, transaction risk, recovery strategies, and governed actions.

---

# 🎯 Problem Statement

Digital commerce has several challenges on both the customer and merchant sides.

## Customer-Side Problems

Customers may need to:

- Search through multiple products
- Understand product options
- Manually manage shopping carts
- Navigate through multiple checkout steps
- Correct product or quantity mistakes
- Understand what they are purchasing before payment

This can make the buying experience slower and less conversational.

For example, a customer who wants a laptop backpack may have to manually search the catalog, identify the correct product, add it to the cart, verify the quantity, and then navigate through checkout.

MerchantOps AI reduces this complexity by allowing the customer to communicate with the system naturally.

---

## Merchant-Side Problems

Merchants may need to:

- Monitor payment failures
- Identify revenue at risk
- Understand transaction risk
- Estimate possible recovery
- Compare recovery strategies
- Determine appropriate actions
- Monitor payment verification
- Process payment webhooks safely
- Maintain operational audit trails

Payment information can contain valuable business signals, but raw payment events alone do not directly tell a merchant what action should be considered.

MerchantOps AI transforms payment information into structured analysis and recommendations through its AI-powered payment intelligence layer.

---

## Overall Problem

The main problem is that customer commerce workflows and merchant payment intelligence are often treated as separate systems.

MerchantOps AI connects them.

```text
Customer Experience
        +
Payment Processing
        +
Payment Intelligence
        +
Governance
```

This creates a more connected and intelligent commerce workflow.

---

# 💡 Solution

MerchantOps AI provides an end-to-end intelligent commerce workflow.

The customer can interact with the system using natural language, while the backend manages product discovery, cart operations, checkout, payment processing, and verification.

The merchant side then receives payment intelligence through specialized AI agents.

```text
                         CUSTOMER
                            │
                            ▼
                  ┌───────────────────┐
                  │     Buyer AI      │
                  │ Natural Language  │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Product Discovery │
                  │ & Recommendation  │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │  Cart Management  │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │     Checkout      │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Razorpay Payment  │
                  └─────────┬─────────┘
                            │
                            ▼
                  ┌───────────────────┐
                  │ Payment           │
                  │ Verification      │
                  └─────────┬─────────┘
                            │
                            ▼
              ┌───────────────────────────┐
              │ Merchant Payment          │
              │ Intelligence              │
              └─────────────┬─────────────┘
                            │
             ┌──────────────┼───────────────┐
             ▼              ▼               ▼
       Revenue Agent    Risk Agent    Simulation Agent
             │              │               │
             └──────────────┼───────────────┘
                            ▼
                    Decision Agent
                            │
                            ▼
                   Action Guardrails
                            │
                            ▼
                     Final Decision
```

The system therefore supports two connected journeys:

### Customer Journey

```text
Natural-Language Request
        ↓
Buyer AI
        ↓
Product Recommendation
        ↓
Cart
        ↓
Checkout
        ↓
Razorpay Payment
        ↓
Payment Verification
```

### Merchant Journey

```text
Payment Data
        ↓
Revenue Analysis
        ↓
Risk Assessment
        ↓
Recovery Simulation
        ↓
AI Decision
        ↓
Governance
        ↓
Audit Trail
```

---

# 🛍️ AI-Powered Agentic Commerce

MerchantOps AI includes a conversational shopping experience where customers can interact with the commerce system using natural language.

The Buyer AI acts as an intelligent shopping assistant instead of requiring the customer to understand the application's internal workflow.

## 🤖 Buyer AI Capabilities

Buyer AI supports:

- Natural-language product search
- Product recommendations
- Product detail retrieval
- Related product suggestions
- Product identification
- Add-to-cart operations
- Cart viewing
- Quantity updates
- Product removal
- Conversational commerce interactions

### Example Interaction

```text
Customer:
Show me backpacks

Buyer AI:
Recommends Laptop Backpack Pro

Customer:
Add Laptop Backpack Pro

Buyer AI:
Adds the product to the cart

Customer:
Show my cart

Buyer AI:
Displays the current cart and total
```

The customer does not need to know the internal API or database structure.

They can simply communicate what they want.

---

# 🎯 Intelligent Product Discovery

Buyer AI can interpret customer requests and find relevant products from the commerce catalog.

The system supports product information such as:

- Product ID
- Product name
- Category
- Price
- Stock
- Variants
- Variant price
- Variant stock
- Related products

Example products include:

```text
BP001
Laptop Backpack Pro
₹1,499

LS001
Laptop Sleeve
₹499

ORG001
Travel Organizer
₹299
```

The system can also use related-product information to support recommendations.

---

# 🛒 Intelligent Cart Management

MerchantOps AI provides a dedicated cart workflow for Buyer AI.

Cart operations include:

```text
Create Cart
    ↓
Add Product
    ↓
Update Quantity
    ↓
View Cart
    ↓
Remove Product
    ↓
Calculate Total
    ↓
Checkout
```

The cart stores:

- Cart ID
- Product ID
- Product name
- Category
- Variant
- Quantity
- Unit price
- Line total
- Subtotal
- Discount
- Tax
- Final total
- Currency

Example:

```text
Laptop Backpack Pro
Quantity: 2
Unit Price: ₹1,499
Line Total: ₹2,998
```

The backend uses exact product identifiers for cart operations to reduce ambiguity when products have similar names.

---

# 💳 Buyer Checkout

The Buyer AI commerce experience connects directly to the checkout workflow.

When the customer chooses to checkout, the backend uses the current cart as the source of truth for the payable amount.

The checkout flow is:

```text
Buyer AI
    ↓
Shopping Cart
    ↓
Cart Total
    ↓
Checkout Request
    ↓
Razorpay Order Creation
    ↓
Razorpay Checkout
```

The checkout process collects:

- Customer name
- Customer email
- Customer phone

The backend then creates a Razorpay order using the cart total.

This ensures that the payment amount is based on the actual cart rather than a manually supplied frontend value.

---

# 💰 Razorpay Integration

MerchantOps AI integrates with Razorpay Test Mode for payment processing.

Implemented capabilities include:

- Razorpay order creation
- Razorpay Checkout integration
- Payment processing
- Payment signature verification
- HMAC-SHA256 verification
- Trusted payment retrieval
- Payment status validation
- Payment verification persistence
- Razorpay webhook processing
- Payment lifecycle tracking

The complete payment journey is:

```text
Cart
 ↓
Checkout
 ↓
Razorpay Order
 ↓
Razorpay Payment
 ↓
Payment Verification
 ↓
Verified Payment
```

---

# ✅ Payment Verification

MerchantOps AI does not rely only on the frontend response after a payment.

After the customer completes the payment, the system performs a separate verification process.

```text
Razorpay Checkout
        ↓
Payment Completed
        ↓
Signature Verification
        ↓
Trusted Payment Retrieval
        ↓
Payment Validation
        ↓
Verification Event
        ↓
Payment Verified
```

The demonstrated flow successfully reaches:

```text
Payment Successful
        ↓
Payment Verified ✅
```

---

# 🔐 Payment Security

Payment verification uses cryptographic signature validation.

The system uses:

```text
HMAC-SHA256
```

for payment signature verification.

Sensitive credentials should be provided through environment variables.

Required configuration includes:

```text
DATABASE_URL
RAZORPAY_KEY_ID
RAZORPAY_KEY_SECRET
RAZORPAY_WEBHOOK_SECRET
```

Sensitive credentials should never be committed to the repository.

---

# 🔔 Razorpay Webhooks

MerchantOps AI supports Razorpay webhook processing.

Webhook endpoint:

```text
POST /webhooks/razorpay
```

The webhook workflow is:

```text
Razorpay Webhook
        ↓
Signature Verification
        ↓
Event ID Extraction
        ↓
Duplicate Detection
        ↓
Webhook Processing
        ↓
Database Persistence
        ↓
Audit Trail
```

Supported payment lifecycle events include:

```text
payment.authorized
payment.captured
payment.failed
```

Webhook events can be viewed through:

```text
GET /webhooks/events
```

---

# 🔐 Webhook Idempotency

Webhook processing uses the Razorpay event ID as an idempotency key.

Conceptually:

```text
Webhook Event
      ↓
Event ID
      ↓
Already Exists?
     /     \
   YES      NO
    ↓        ↓
 Ignore    Process
             ↓
          Persist
```

This prevents duplicate webhook events from being processed repeatedly.

---

# 📈 Payment Intelligence

MerchantOps AI goes beyond simply accepting payments.

The platform analyses payment information to help merchants understand:

- Payment failures
- Revenue at risk
- Recovery opportunities
- Transaction risk
- Recovery probability
- Expected recovery value
- Decision confidence
- Recommended action

Possible recovery actions include:

```text
RETRY_NOW
RETRY_LATER
REVIEW
DO_NOTHING
```

---

# 🤖 Agentic Payment Intelligence

The merchant-side intelligence layer uses specialized AI agents.

```text
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
```

Each stage contributes information to the final recommendation.

The system can produce:

```text
Risk Score
Risk Level
Recovery Probability
Expected Recovery
Simulation Results
Decision Confidence
Final Action
Decision Explanation
```

---

# 💰 Revenue Agent

The Revenue Agent evaluates the potential financial opportunity associated with failed payments.

It helps answer questions such as:

```text
How much revenue is potentially at risk?

How much could potentially be recovered?

Which transactions deserve attention?
```

Example:

```text
Payment Amount: ₹9,875
Risk Score: 0.42
Risk Level: MEDIUM
Recovery Probability: 38.8%
Expected Recovery: ₹3,829
Final Decision: RETRY_LATER
```

The figures above represent a demonstration scenario and are not live financial statistics.

---

# ⚠️ Risk Agent

The Risk Agent evaluates transaction-level risk.

It produces a structured risk assessment that can be consumed by the decision layer.

The basic flow is:

```text
Transaction
     ↓
Risk Analysis
     ↓
Risk Score
     ↓
Risk Level
     ↓
Decision Input
```

Risk levels include:

```text
LOW
MEDIUM
HIGH
```

---

# 🧪 Simulation Agent

The Simulation Agent evaluates potential recovery strategies before a final action is considered.

It helps estimate:

- Recovery probability
- Expected recovery
- Potential outcomes
- Alternative recovery scenarios

Conceptually:

```text
Failed Payment
      ↓
Candidate Strategies
      ↓
Simulation
      ↓
Expected Outcomes
      ↓
Decision Agent
```

---

# 🧠 Decision Agent

The Decision Agent combines multiple signals before generating a final recommendation.

Inputs include:

```text
Risk
Recovery Opportunity
Simulation Results
Confidence
Governance Policy
```

Possible decisions are:

```text
RETRY_NOW
RETRY_LATER
REVIEW
DO_NOTHING
```

Example:

```text
Risk Score: 0.42
Risk Level: MEDIUM
Recovery Probability: 38.8%
Expected Recovery: ₹3,829
Decision: RETRY_LATER
Confidence: 58%
```

---

# 🛡️ Governance & Safety

AI recommendations do not automatically become unrestricted actions.

MerchantOps AI includes a governance layer between AI recommendations and execution.

Supported governance modes include:

```text
MERCHANT_APPROVAL
SCHEDULED_TEST_ACTION
BLOCKED
NO_ACTION
```

The governance layer can:

- Require merchant approval
- Block high-risk actions
- Permit controlled test actions
- Evaluate action policies
- Classify execution modes
- Record audit events

Example:

```text
High Risk Transaction
        ↓
Risk Assessment
        ↓
DO_NOTHING
        ↓
BLOCKED
```

Another example:

```text
Strong Recovery Opportunity
        ↓
RETRY_NOW
        ↓
MERCHANT_APPROVAL
```

---

# 🧠 Explainable AI Decisions

MerchantOps AI provides structured information explaining AI-generated recommendations.

Decision details can include:

```text
Payment ID
Order ID
Customer
Amount
Payment Method
Failure Reason
Risk Score
Expected Recovery
Confidence
Final Decision
Decision Reason
Policy Mode
```

This allows merchants to understand the reasoning behind a recommendation rather than receiving only an unexplained action.

---

# 📊 Streamlit Merchant Dashboard

MerchantOps AI includes an interactive Streamlit dashboard connected to the FastAPI backend.

The dashboard provides views for:

## Merchant Operations Overview

Displays:

- Total payments
- Failed payments
- Success rate
- Failure rate
- Revenue at risk

## Razorpay Activity

Displays:

- Verified payments
- Payment verification events
- Webhook events
- Webhook processing activity

## AI Executive Summary

Displays:

- Revenue at risk
- Recovery candidates
- Expected recovery
- AI decisions

## AI Action Recommendations

Shows:

```text
RETRY_NOW
RETRY_LATER
REVIEW
DO_NOTHING
```

## AI Governance & Safety

Displays:

- Merchant approvals
- Allowed actions
- Blocked actions
- Scheduled test actions

## Decision Explorer

Allows decision records to be explored using filters such as:

- Action
- Risk level
- Row limit

## Merchant Approval Queue

Displays decisions that require merchant approval.

## Decision Details & Explainability

Displays detailed decision information.

## Simulation Analysis

Displays recovery simulation scenarios and expected recovery values.

## Audit Trail

Displays important system events recorded by the backend.

---

# 🗄️ PostgreSQL Persistence

Production persistence uses PostgreSQL.

Important data areas include:

```text
audit_logs
webhook_events
```

Audit records can contain:

- Timestamp
- Event type
- Payment ID
- Decision
- Action
- Risk level
- Approval requirement
- Execution mode
- Status
- Structured details

Structured information is stored using PostgreSQL JSONB where appropriate.

---

# 📋 Audit Logging

MerchantOps AI maintains an audit trail for important system events.

This provides visibility into:

```text
What happened?
When did it happen?
Which payment was involved?
What decision was generated?
What action was recommended?
Was approval required?
Was the action blocked?
```

Auditability is an important part of the system's governance architecture.

---

# 🌐 REST API

## Health

```text
GET /health
GET /health/database
GET /activity/stats
```

## Buyer AI

```text
POST /buyer/chat
```

## Product Catalog

```text
GET /catalog
GET /catalog/{product_id}
```

## Cart

```text
POST /cart
GET /cart/{cart_id}
POST /cart/{cart_id}/items
PATCH /cart/{cart_id}/items/{product_id}
DELETE /cart/{cart_id}/items/{product_id}
POST /cart/{cart_id}/calculate
POST /cart/{cart_id}/checkout
```

## Payments

```text
GET /payments
GET /payments/verified

POST /razorpay/create-order
POST /razorpay/verify-payment
```

## AI Analysis

```text
GET /analyze
GET /decisions
```

## Audit

```text
GET /audit
```

## Webhooks

```text
GET /webhooks/events
POST /webhooks/razorpay
```

---

# 🧪 Testing

The project includes automated tests covering important payment-intelligence and infrastructure components.

Test coverage includes:

- Action Tools
- Audit Logging
- Decision Agent
- Orchestrator
- Payment Adapter
- Payment Provider
- Payment Verification
- Revenue Agent
- Risk Agent
- Simulation Agent
- Razorpay Webhook Handling
- Webhook Event Persistence
- Webhook Processing

Current verified result:

```text
27 passed
```

Run:

```bash
python -m pytest -q
```

Expected result:

```text
27 passed
```

---

# ✅ Verified End-to-End Demonstration

The project has been tested through the following workflow:

```text
1. Open Buyer AI
        ↓
2. Search for a product
        ↓
3. Receive an AI recommendation
        ↓
4. Add product to cart
        ↓
5. View cart
        ↓
6. Manage cart items
        ↓
7. Open checkout
        ↓
8. Create Razorpay Test Mode order
        ↓
9. Complete payment
        ↓
10. Verify payment
        ↓
11. Display Payment Verified
```

Example demonstration:

```text
Product:
Laptop Backpack Pro

Quantity:
1

Price:
₹1,499

Checkout:
₹1,499

Payment:
Razorpay Test Mode

Result:
Payment Verified ✅
```

---

# 🧩 Build Challenges & Solutions

Building the project required integrating multiple systems while keeping the existing payment-intelligence functionality stable.

## 1. Natural-Language Product Identification

Customers may refer to products using names rather than internal product IDs.

### Solution

The Buyer AI resolves products from natural-language requests and uses exact product identifiers for cart operations.

---

## 2. Quantity Extraction

A challenge occurred when numeric values inside product descriptions could be incorrectly interpreted as quantities.

For example:

```text
15.6-inch Laptop Sleeve
```

The `15.6` describes the product and should not become a quantity.

### Solution

The quantity extraction logic was improved to prioritize explicit quantity expressions such as:

```text
quantity 2
qty 2
add 2 units
make it 3
```

while avoiding unrelated numbers contained in product descriptions.

---

## 3. Correct Cart Product Selection

Products with similar names could create ambiguity during cart operations.

### Solution

Cart operations use exact product IDs to make product selection more reliable.

---

## 4. Cart API Integration

The Buyer AI required a dedicated cart layer instead of relying only on frontend state.

### Solution

Dedicated APIs were implemented for:

```text
Cart creation
Cart retrieval
Product addition
Quantity updates
Product removal
Cart calculation
Checkout
```

---

## 5. Checkout Integration

The cart needed to connect to Razorpay while ensuring the payment amount matched the actual cart.

### Solution

The backend uses the cart total as the authoritative checkout amount before creating the Razorpay payment order.

---

## 6. Payment Verification

A frontend success response alone is not sufficient for a reliable payment workflow.

### Solution

Razorpay payment signatures are verified and trusted payment information is retrieved before treating the transaction as verified.

---

## 7. Webhook Reliability

Payment webhooks can potentially be delivered more than once.

### Solution

Razorpay event IDs are used for idempotency so duplicate events are not processed repeatedly.

---

# ⚙️ Technology Stack

## Backend

```text
Python
FastAPI
REST APIs
Pandas
```

## AI / Decisioning

```text
Agentic AI Workflow
Revenue Analysis
Risk Scoring
Recovery Simulation
Decision Automation
Explainable Decisioning
Governance Policies
```

## Commerce

```text
Buyer AI
Product Catalog
Product Recommendation
Cart Management
Checkout Workflow
```

## Payments

```text
Razorpay API
Razorpay Checkout
Razorpay Test Mode
Payment Verification
Razorpay Webhooks
HMAC-SHA256
```

## Database

```text
PostgreSQL
JSONB
```

## Frontend

```text
Streamlit
HTML
JavaScript
```

## Testing

```text
Pytest
```

## Deployment & Version Control

```text
Render
Streamlit
Git
GitHub
```

---

# 📁 Project Structure

```text
MerchantOps-AI/
│
├── backend/
│   ├── agents/
│   │   ├── buyer_agent.py
│   │   ├── offer_agent.py
│   │   ├── revenue_agent.py
│   │   ├── risk_agent.py
│   │   ├── simulation_agent.py
│   │   ├── decision_agent.py
│   │   └── orchestrator.py
│   │
│   ├── api/
│   │   ├── buyer.py
│   │   ├── catalog.py
│   │   ├── cart.py
│   │   └── offers.py
│   │
│   ├── commerce/
│   │   ├── buyer_tools.py
│   │   ├── catalog.py
│   │   ├── cart.py
│   │   └── offer_tools.py
│   │
│   ├── database/
│   │   ├── postgres.py
│   │   ├── audit.py
│   │   └── webhook_events.py
│   │
│   ├── tools/
│   │   ├── payment_provider.py
│   │   ├── action_tools.py
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
│   ├── checkout.html
│   └── payment_adapter.py
│
├── data/
│   └── catalog.json
│
├── tests/
│
├── requirements.txt
└── README.md
```

---

# 🚀 Local Setup

## 1. Clone Repository

```bash
git clone https://github.com/AbhishekRBiradar/MerchantOps-AI.git
cd MerchantOps-AI
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create a `.env` file:

```text
DATABASE_URL=your_postgresql_connection_string

RAZORPAY_KEY_ID=your_razorpay_test_key_id

RAZORPAY_KEY_SECRET=your_razorpay_test_key_secret

RAZORPAY_WEBHOOK_SECRET=your_razorpay_webhook_secret
```

Never commit `.env` to GitHub.

---

# ▶️ Run Backend

```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

# ▶️ Run Streamlit Dashboard

```bash
streamlit run dashboard/app.py
```

---

# ▶️ Run Buyer Checkout Page

```bash
python -m http.server 5500
```

Checkout page:

```text
http://127.0.0.1:5500/razorpay/checkout.html
```

Buyer cart checkout:

```text
http://127.0.0.1:5500/razorpay/checkout.html?cart_id=YOUR_CART_ID&api=local
```

---

# ☁️ Deployment

## Backend

The FastAPI backend can be deployed using Render.

Production API:

```text
https://merchantops-ai-api.onrender.com
```

## Dashboard

The Streamlit dashboard communicates with the FastAPI backend.

```text
Streamlit Dashboard
        ↓
FastAPI API
        ↓
PostgreSQL
```

---

# 📌 Project Status

## Agentic Commerce

```text
Buyer AI                         ✅
Natural-Language Product Search ✅
Product Recommendation          ✅
Product Details                 ✅
Related Products                ✅
Cart Creation                   ✅
Add to Cart                     ✅
Cart Viewing                    ✅
Quantity Management             ✅
Product Removal                 ✅
Buyer Checkout                  ✅
Razorpay Test Payment           ✅
Payment Verification            ✅
```

## Payment Intelligence

```text
FastAPI Backend                 ✅
Payment Intelligence            ✅
Revenue Analysis                ✅
Risk Analysis                   ✅
Recovery Simulation              ✅
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
Automated Testing               ✅
27/27 Tests Passing             ✅
```

---

# 🎥 5-Minute Demo Flow

The recommended demonstration flow is:

```text
00:00
Project Introduction

00:20
Problem Statement

01:00
Buyer AI Product Search

01:30
Product Recommendation

01:50
Add Product to Cart

02:10
Cart Management

02:30
Checkout

02:50
Razorpay Test Payment

03:10
Payment Verified

03:20
Merchant Payment Intelligence

04:10
Build Challenges

04:40
Final Summary
```

The demonstration should show the actual application while explaining the purpose of each step.

---

# 🔮 Future Enhancements

Potential future enhancements include:

- Persistent customer profiles
- Personalized recommendations
- Advanced inventory intelligence
- Real-time stock-aware recommendations
- More sophisticated offer optimization
- Persistent production cart storage
- Customer purchase history
- Advanced fraud detection
- Real-time payment analytics
- Multi-payment-provider support
- Multi-agent orchestration
- Production-scale event streaming
- Advanced merchant decision automation
- Human-in-the-loop approval workflows
- Advanced observability
- Advanced explainability and monitoring

---

# ⚠️ Limitations

Razorpay integration currently uses Test Mode.

The AI recovery and decisioning components are intended for:

- Demonstration
- Research
- Academic use
- Portfolio presentation
- Controlled automation testing

Real-world financial, fraud, risk, compliance, and regulatory systems would require additional validation, monitoring, security controls, compliance processes, human oversight, and production testing.

---

# 👨‍💻 Author

## Abhishek Rajkumar Biradar

AI/ML | Python | Backend Development | Data & AI Systems | Agentic AI

GitHub:

https://github.com/AbhishekRBiradar

Project Repository:

https://github.com/AbhishekRBiradar/MerchantOps-AI

---

# 📄 Disclaimer

MerchantOps AI is a portfolio and academic engineering project demonstrating agentic commerce, AI-assisted product discovery, cart management, payment integration, payment verification, payment intelligence, revenue recovery analysis, risk assessment, recovery simulation, explainable decisioning, governance, webhook processing, and production-style backend architecture using Razorpay Test Mode.

It is not intended to replace production financial risk systems, fraud detection systems, payment authorization systems, compliance systems, or regulatory controls.

---

# ⭐ Final Project Summary

MerchantOps AI combines **Agentic Commerce + Payment Intelligence** into one platform.

The customer-facing side enables:

```text
Ask
 ↓
Discover
 ↓
Choose
 ↓
Cart
 ↓
Checkout
 ↓
Pay
 ↓
Verify
```

The merchant-facing side enables:

```text
Analyze
 ↓
Assess
 ↓
Simulate
 ↓
Decide
 ↓
Govern
 ↓
Audit
```

Together:

```text
                 MERCHANTOPS AI

        ┌─────────────────────────┐
        │    AGENTIC COMMERCE     │
        │                         │
        │ Buyer AI                │
        │ Product Discovery       │
        │ Recommendation          │
        │ Cart                    │
        │ Checkout                │
        │ Razorpay                │
        │ Payment Verification    │
        └────────────┬────────────┘
                     │
                     ▼
        ┌─────────────────────────┐
        │   PAYMENT INTELLIGENCE  │
        │                         │
        │ Revenue                 │
        │ Risk                    │
        │ Simulation              │
        │ Decision                │
        │ Governance              │
        │ Audit                   │
        └─────────────────────────┘
```

MerchantOps AI demonstrates how AI can move commerce from a simple transaction workflow toward an intelligent, conversational, governed, and decision-aware system.