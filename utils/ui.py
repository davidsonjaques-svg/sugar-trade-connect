import streamlit as st

BRAND = {
    "primary": "#1B4332",       # deep forest green - sugar cane
    "accent": "#40916C",        # mid green
    "highlight": "#D4A017",     # golden amber - raw sugar
    "bg": "#F8F6F1",            # warm cream
    "surface": "#FFFFFF",
    "text": "#1A1A1A",
    "muted": "#6B7280",
    "danger": "#C0392B",
    "success": "#1B4332",
    "warning": "#D4A017",
    "border": "#E5E0D5",
}

def inject_global_css():
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&family=Inter:wght@300;400;500;600&display=swap');

    /* ── Reset & Base ── */
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {BRAND['bg']} !important;
        font-family: 'Inter', sans-serif;
        color: {BRAND['text']};
    }}
    [data-testid="stSidebar"] {{
        background-color: {BRAND['primary']} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label {{
        color: #d1fae5 !important;
    }}

    /* ── Header Brand ── */
    .brand-header {{
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 20px 0 8px 0;
        border-bottom: 2px solid {BRAND['highlight']};
        margin-bottom: 28px;
    }}
    .brand-logo {{
        width: 44px;
        height: 44px;
        background: {BRAND['highlight']};
        border-radius: 8px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
    }}
    .brand-name {{
        font-family: 'Playfair Display', serif;
        font-size: 22px;
        font-weight: 700;
        color: {BRAND['primary']};
        line-height: 1.1;
    }}
    .brand-sub {{
        font-size: 11px;
        color: {BRAND['muted']};
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    /* ── Page Title ── */
    .page-title {{
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 700;
        color: {BRAND['primary']};
        margin-bottom: 4px;
    }}
    .page-subtitle {{
        font-size: 14px;
        color: {BRAND['muted']};
        margin-bottom: 28px;
    }}

    /* ── Cards ── */
    .card {{
        background: {BRAND['surface']};
        border: 1px solid {BRAND['border']};
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
    }}
    .card-accent {{
        border-left: 4px solid {BRAND['highlight']};
    }}
    .card-success {{
        border-left: 4px solid {BRAND['success']};
        background: #f0fdf4;
    }}
    .card-warning {{
        border-left: 4px solid {BRAND['warning']};
        background: #fffbeb;
    }}
    .card-danger {{
        border-left: 4px solid {BRAND['danger']};
        background: #fff5f5;
    }}

    /* ── Status Badges ── */
    .badge {{
        display: inline-block;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.02em;
    }}
    .badge-pending {{ background: #FEF3C7; color: #92400E; }}
    .badge-payment_confirmed {{ background: #D1FAE5; color: #065F46; }}
    .badge-in_transit {{ background: #DBEAFE; color: #1E40AF; }}
    .badge-delivered {{ background: #D1FAE5; color: #065F46; }}
    .badge-pending_payment {{ background: #FEE2E2; color: #991B1B; }}
    .badge-cancelled {{ background: #F3F4F6; color: #374151; }}

    /* ── Stat Cards ── */
    .stat-grid {{
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
        gap: 16px;
        margin-bottom: 28px;
    }}
    .stat-card {{
        background: {BRAND['surface']};
        border: 1px solid {BRAND['border']};
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }}
    .stat-value {{
        font-family: 'Playfair Display', serif;
        font-size: 28px;
        font-weight: 700;
        color: {BRAND['primary']};
        line-height: 1;
    }}
    .stat-label {{
        font-size: 12px;
        color: {BRAND['muted']};
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}
    .stat-accent .stat-value {{ color: {BRAND['highlight']}; }}

    /* ── Timeline ── */
    .timeline {{
        position: relative;
        padding-left: 28px;
    }}
    .timeline::before {{
        content: '';
        position: absolute;
        left: 8px;
        top: 0;
        bottom: 0;
        width: 2px;
        background: {BRAND['border']};
    }}
    .timeline-item {{
        position: relative;
        margin-bottom: 20px;
    }}
    .timeline-dot {{
        position: absolute;
        left: -24px;
        top: 4px;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: {BRAND['accent']};
        border: 2px solid {BRAND['surface']};
        box-shadow: 0 0 0 2px {BRAND['accent']};
    }}
    .timeline-dot.active {{
        background: {BRAND['highlight']};
        box-shadow: 0 0 0 2px {BRAND['highlight']};
    }}
    .timeline-time {{
        font-size: 11px;
        color: {BRAND['muted']};
        margin-bottom: 2px;
    }}
    .timeline-title {{
        font-weight: 600;
        font-size: 14px;
        color: {BRAND['primary']};
    }}
    .timeline-desc {{
        font-size: 13px;
        color: {BRAND['muted']};
    }}

    /* ── Streamlit overrides ── */
    .stButton > button {{
        background: {BRAND['primary']} !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        transition: all 0.2s !important;
    }}
    .stButton > button:hover {{
        background: {BRAND['accent']} !important;
        transform: translateY(-1px);
    }}
    .stTextInput > div > div > input,
    .stSelectbox > div > div,
    .stTextArea > div > div > textarea,
    .stNumberInput > div > div > input {{
        border-radius: 8px !important;
        border: 1px solid {BRAND['border']} !important;
    }}
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div:focus,
    .stTextArea > div > div > textarea:focus {{
        border-color: {BRAND['accent']} !important;
        box-shadow: 0 0 0 2px rgba(64,145,108,0.15) !important;
    }}
    div[data-testid="stMetric"] {{
        background: {BRAND['surface']};
        border: 1px solid {BRAND['border']};
        border-radius: 12px;
        padding: 16px;
    }}
    [data-testid="stMetricValue"] {{
        color: {BRAND['primary']} !important;
        font-family: 'Playfair Display', serif !important;
    }}
    .stAlert {{
        border-radius: 10px !important;
    }}
    div[data-testid="stForm"] {{
        background: {BRAND['surface']};
        padding: 28px;
        border-radius: 14px;
        border: 1px solid {BRAND['border']};
    }}
    </style>
    """, unsafe_allow_html=True)

def brand_header():
    st.markdown("""
    <div class="brand-header">
        <div class="brand-logo">🌾</div>
        <div>
            <div class="brand-name">Sugar Trade Connect</div>
            <div class="brand-sub">Premium Sugar Trading Platform · South Africa</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def page_title(title, subtitle=""):
    st.markdown(f"""
    <div class="page-title">{title}</div>
    <div class="page-subtitle">{subtitle}</div>
    """, unsafe_allow_html=True)

def status_badge(status):
    labels = {
        "pending_payment": "Awaiting Payment",
        "payment_pending": "Payment Pending",
        "payment_confirmed": "Payment Confirmed",
        "processing": "Processing",
        "dispatched": "Dispatched",
        "in_transit": "In Transit",
        "out_for_delivery": "Out for Delivery",
        "delivered": "Delivered",
        "cancelled": "Cancelled",
        "order_confirmed": "Order Confirmed",
        "awaiting_dispatch": "Awaiting Dispatch",
    }
    label = labels.get(status, status.replace("_", " ").title())
    css_class = f"badge-{status}" if status in [
        "pending_payment", "payment_confirmed", "in_transit", "delivered", "pending", "cancelled"
    ] else "badge-pending"
    return f'<span class="badge {css_class}">{label}</span>'

def card(content_html, variant=""):
    css = f"card {f'card-{variant}' if variant else ''}"
    st.markdown(f'<div class="{css}">{content_html}</div>', unsafe_allow_html=True)

def format_zar(amount):
    return f"R {amount:,.2f}"

def require_login():
    if "customer" not in st.session_state or not st.session_state.customer:
        st.warning("Please log in to access this page.")
        st.stop()
    return st.session_state.customer
