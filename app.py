import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from utils.database import init_db, authenticate, create_customer
from utils.ui import inject_global_css, brand_header, page_title, BRAND

st.set_page_config(
    page_title="Sugar Trade Connect",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
inject_global_css()

# ── Session defaults ──────────────────────────────────────────────────────────
if "customer" not in st.session_state:
    st.session_state.customer = None
if "page" not in st.session_state:
    st.session_state.page = "login"
if "active_order_id" not in st.session_state:
    st.session_state.active_order_id = None

# ── Sidebar navigation ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 20px 0 16px 0;'>
        <div style='font-size:40px;'>🌾</div>
        <div style='font-family:"Playfair Display",serif; font-size:18px; font-weight:700; color:#D4A017;'>
            Sugar Trade Connect
        </div>
        <div style='font-size:11px; color:#86efac; letter-spacing:0.08em; text-transform:uppercase; margin-top:4px;'>
            Premium Trading Platform
        </div>
    </div>
    <hr style='border-color: rgba(255,255,255,0.15); margin: 8px 0 20px 0;'>
    """, unsafe_allow_html=True)

    if st.session_state.customer:
        cust = st.session_state.customer
        st.markdown(f"""
        <div style='background:rgba(255,255,255,0.08); border-radius:10px; padding:14px; margin-bottom:20px;'>
            <div style='font-size:12px; color:#86efac; text-transform:uppercase; letter-spacing:0.05em;'>Logged in as</div>
            <div style='font-weight:600; font-size:15px; margin-top:4px;'>{cust['full_name']}</div>
            <div style='font-size:12px; color:#86efac;'>{cust['email']}</div>
        </div>
        """, unsafe_allow_html=True)

        nav_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("📦", "Place Order", "place_order"),
            ("💳", "My Orders", "my_orders"),
            ("🚚", "Track Shipment", "track"),
            ("👤", "My Profile", "profile"),
        ]
        for icon, label, key in nav_items:
            active = st.session_state.page == key
            if st.button(f"{icon}  {label}", key=f"nav_{key}",
                         use_container_width=True,
                         type="primary" if active else "secondary"):
                st.session_state.page = key
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚪  Log Out", use_container_width=True):
            st.session_state.customer = None
            st.session_state.page = "login"
            st.rerun()
    else:
        st.markdown("""
        <div style='color:#86efac; font-size:13px; text-align:center; padding: 8px 0;'>
            Log in to access your trading account
        </div>
        """, unsafe_allow_html=True)

# ── Routing ───────────────────────────────────────────────────────────────────
page = st.session_state.page

if not st.session_state.customer and page not in ("login", "register"):
    page = "login"

if page == "login":
    col_l, col_m, col_r = st.columns([1, 1.4, 1])
    with col_m:
        st.markdown("""
        <div style='text-align:center; padding: 40px 0 32px 0;'>
            <div style='font-size:56px;'>🌾</div>
            <div style='font-family:"Playfair Display",serif; font-size:32px; font-weight:700;
                        color:#1B4332; margin-top:8px;'>Sugar Trade Connect</div>
            <div style='color:#6B7280; font-size:14px; margin-top:6px;'>
                South Africa's Premium Sugar Trading Portal
            </div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            st.markdown("### Sign In")
            email = st.text_input("Email address", placeholder="you@company.co.za")
            password = st.text_input("Password", type="password", placeholder="••••••••")
            submitted = st.form_submit_button("Sign In →", use_container_width=True)

        if submitted:
            if not email or not password:
                st.error("Please enter your email and password.")
            else:
                customer = authenticate(email.strip().lower(), password)
                if customer:
                    st.session_state.customer = customer
                    st.session_state.page = "dashboard"
                    st.rerun()
                else:
                    st.error("Invalid email or password. Please try again.")

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("""
            <div style='background:#f0fdf4; border-radius:10px; padding:14px; font-size:13px;
                        border:1px solid #d1fae5;'>
                <strong>Demo Account</strong><br>
                📧 demo@sugarco.co.za<br>
                🔑 demo123
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown("""
            <div style='background:#fffbeb; border-radius:10px; padding:14px; font-size:13px;
                        border:1px solid #fef3c7; cursor:pointer;'>
                <strong>New customer?</strong><br>
                Create your account to start trading
            </div>
            """, unsafe_allow_html=True)
            if st.button("Create Account →", use_container_width=True):
                st.session_state.page = "register"
                st.rerun()

elif page == "register":
    col_l, col_m, col_r = st.columns([1, 1.4, 1])
    with col_m:
        brand_header()
        page_title("Create Account", "Join Sugar Trade Connect to start placing orders")

        with st.form("register_form"):
            full_name = st.text_input("Full Name *", placeholder="John Smith")
            email = st.text_input("Email Address *", placeholder="john@company.co.za")
            company = st.text_input("Company Name", placeholder="Smith Trading (Pty) Ltd")
            phone = st.text_input("Phone Number *", placeholder="+27 82 000 0000")
            address = st.text_area("Delivery / Billing Address *",
                                   placeholder="123 Street, City, Province, Postal Code",
                                   height=80)
            st.markdown("---")
            password = st.text_input("Password *", type="password",
                                     placeholder="Minimum 6 characters")
            password2 = st.text_input("Confirm Password *", type="password",
                                      placeholder="Repeat password")
            submitted = st.form_submit_button("Create Account →", use_container_width=True)

        if submitted:
            errors = []
            if not full_name: errors.append("Full name is required.")
            if not email: errors.append("Email is required.")
            if not phone: errors.append("Phone number is required.")
            if not address: errors.append("Address is required.")
            if not password: errors.append("Password is required.")
            if len(password) < 6: errors.append("Password must be at least 6 characters.")
            if password != password2: errors.append("Passwords do not match.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                ok, msg = create_customer(email.strip().lower(), password,
                                          full_name.strip(), company.strip(),
                                          phone.strip(), address.strip())
                if ok:
                    st.success("Account created! Please sign in.")
                    if st.button("Go to Sign In"):
                        st.session_state.page = "login"
                        st.rerun()
                else:
                    st.error(msg)

        if st.button("← Back to Sign In"):
            st.session_state.page = "login"
            st.rerun()

elif page == "dashboard":
    from pages.dashboard import render
    render()

elif page == "place_order":
    from pages.place_order import render
    render()

elif page == "my_orders":
    from pages.my_orders import render
    render()

elif page == "payment":
    from pages.payment import render
    render()

elif page == "track":
    from pages.track import render
    render()

elif page == "profile":
    from pages.profile import render
    render()

else:
    st.session_state.page = "login"
    st.rerun()
