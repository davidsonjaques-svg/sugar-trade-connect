# 🌾 Sugar Trade Connect

A full-stack, production-ready B2B sugar trading portal built with **Streamlit** and **Python**. Replaces WhatsApp-based ordering with a professional digital workflow — from customer login through order placement, payment, and shipment tracking.

---

## Features

| Module | What it does |
|---|---|
| **Auth** | Customer registration & login with hashed passwords |
| **Dashboard** | Live order stats, quick actions, recent order feed |
| **Place Order** | Full order form: product type, grade, quantity, VAT calc, delivery details, T&Cs |
| **Order Confirmation** | Immediate receipt — order held until payment confirmed |
| **Payment Gateway** | Simulated secure card/EFT gateway with validation |
| **Proof of Payment** | Manual PoP upload (JPG/PNG/PDF) + **Claude AI visual verification** |
| **Shipment Tracking** | End-to-end timeline from dispatch → delivered, with milestone progress bar |
| **Profile** | Edit personal details, change password, view account stats |

---

## Stack

- **Frontend/Backend**: [Streamlit](https://streamlit.io)
- **Database**: SQLite (zero-config, file-based, production-upgradeable to PostgreSQL)
- **AI Verification**: [Anthropic Claude](https://anthropic.com) via `anthropic` Python SDK
- **Styling**: Custom CSS with Google Fonts (Playfair Display + Inter)

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/sugar-trade-connect.git
cd sugar-trade-connect
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set your Anthropic API key

The AI proof-of-payment verification requires an Anthropic API key.

**Option A — environment variable:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

**Option B — Streamlit secrets** (recommended for cloud deployment):

Create `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

### 4. Run the app

```bash
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## Demo Credentials

| Email | Password |
|---|---|
| demo@sugarco.co.za | demo123 |

---

## Project Structure

```
sugar-trade-connect/
├── app.py                    # Entry point, routing, login/register
├── requirements.txt
├── .streamlit/
│   └── config.toml           # Theme & server config
├── pages/
│   ├── dashboard.py          # Customer dashboard
│   ├── place_order.py        # Order form
│   ├── my_orders.py          # Order list & detail view
│   ├── payment.py            # Gateway + PoP upload + AI verification
│   ├── track.py              # Shipment tracking timeline
│   └── profile.py            # Profile management
├── utils/
│   ├── database.py           # SQLite ORM-lite layer
│   ├── ui.py                 # Design system, CSS, shared components
│   └── pop_verify.py         # Claude AI proof-of-payment analyser
└── data/
    └── sugar_trade.db        # Auto-created on first run
```

---

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io) → New app
3. Select your repo, branch `main`, file `app.py`
4. Under **Advanced settings → Secrets**, add:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Click **Deploy**

> **Note**: The SQLite database resets on each deployment. For persistent production data, swap `database.py` to use PostgreSQL via `psycopg2` and Streamlit's `st.connection`.

---

## AI Proof-of-Payment Verification

When a customer uploads a PoP image, the app sends it to **Claude claude-sonnet-4-6** with the expected amount and order reference. Claude returns:

- ✅ **APPROVE** — Document is a legitimate PoP, amount matches
- ⚠️ **QUERY** — Uncertain, recommend manual review
- ❌ **REJECT** — Red flags detected (potential fraud/alteration)

Extracted data includes: bank name, sender, beneficiary, amount, date, transaction reference.

---

## Sugar Products & Pricing

| Product | Grade | Price/kg |
|---|---|---|
| White Sugar | Superior Grade A | R 18.50 |
| White Sugar | Grade B Standard | R 16.00 |
| Raw Sugar | ICUMSA 600 | R 14.00 |
| Brown Sugar | Demerara | R 19.00 |
| Speciality | Icing Sugar | R 24.00 |
| *(+ more)* | | |

VAT @ 15% is automatically calculated on all orders.

---

## License

MIT — free to use, modify, and deploy commercially.
