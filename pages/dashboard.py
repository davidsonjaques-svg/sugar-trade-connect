import streamlit as st
from utils.ui import inject_global_css, brand_header, page_title, status_badge, format_zar, require_login, BRAND
from utils.database import get_orders_by_customer, get_shipment_by_order

def render():
    inject_global_css()
    customer = require_login()

    brand_header()
    page_title(f"Welcome back, {customer['full_name'].split()[0]}",
               "Here's your trading activity at a glance")

    orders = get_orders_by_customer(customer["id"])

    # ── Stats ────────────────────────────────────────────────────────────────
    total_orders = len(orders)
    total_value = sum(o["total_amount"] for o in orders)
    pending = sum(1 for o in orders if o["status"] == "pending_payment")
    confirmed = sum(1 for o in orders if o["status"] == "payment_confirmed")
    delivered = sum(1 for o in orders if o["status"] == "delivered")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders", total_orders)
    with col2:
        st.metric("Total Value", format_zar(total_value))
    with col3:
        st.metric("Awaiting Payment", pending)
    with col4:
        st.metric("Confirmed / Active", confirmed)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Quick actions ────────────────────────────────────────────────────────
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("""
        <div class="card card-accent" style="text-align:center; cursor:pointer;">
            <div style="font-size:32px; margin-bottom:8px;">📦</div>
            <div style="font-weight:700; font-size:16px; color:#1B4332;">Place New Order</div>
            <div style="font-size:13px; color:#6B7280; margin-top:4px;">Order sugar in bulk</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Place Order →", key="dash_order", use_container_width=True):
            st.session_state.page = "place_order"
            st.rerun()

    with col_b:
        st.markdown("""
        <div class="card" style="text-align:center; cursor:pointer;">
            <div style="font-size:32px; margin-bottom:8px;">💳</div>
            <div style="font-weight:700; font-size:16px; color:#1B4332;">My Orders</div>
            <div style="font-size:13px; color:#6B7280; margin-top:4px;">View & pay for orders</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("View Orders →", key="dash_orders", use_container_width=True):
            st.session_state.page = "my_orders"
            st.rerun()

    with col_c:
        st.markdown("""
        <div class="card" style="text-align:center; cursor:pointer;">
            <div style="font-size:32px; margin-bottom:8px;">🚚</div>
            <div style="font-weight:700; font-size:16px; color:#1B4332;">Track Shipment</div>
            <div style="font-size:13px; color:#6B7280; margin-top:4px;">Real-time shipment updates</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Track →", key="dash_track", use_container_width=True):
            st.session_state.page = "track"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Recent orders ────────────────────────────────────────────────────────
    st.markdown("### Recent Orders")
    if not orders:
        st.markdown("""
        <div class="card" style="text-align:center; padding:40px;">
            <div style="font-size:40px;">📋</div>
            <div style="font-size:18px; font-weight:600; color:#1B4332; margin-top:12px;">No orders yet</div>
            <div style="color:#6B7280; margin-top:6px;">Place your first order to get started</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for order in orders[:5]:
            badge_html = status_badge(order["status"])
            st.markdown(f"""
            <div class="card" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <div style="font-weight:700; font-size:15px; color:#1B4332;">{order['order_ref']}</div>
                    <div style="font-size:13px; color:#6B7280; margin-top:2px;">
                        {order['product_type']} · {order['grade']} · {order['quantity_kg']:,.0f} kg
                    </div>
                    <div style="font-size:12px; color:#9CA3AF; margin-top:2px;">{order['created_at'][:16]}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-weight:700; font-size:16px;">{format_zar(order['total_amount'])}</div>
                    <div style="margin-top:6px;">{badge_html}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            col_pay, col_view, _ = st.columns([1, 1, 3])
            with col_pay:
                if order["status"] == "pending_payment":
                    if st.button("💳 Pay Now", key=f"pay_{order['id']}", use_container_width=True):
                        st.session_state.active_order_id = order["id"]
                        st.session_state.page = "payment"
                        st.rerun()
            with col_view:
                if st.button("View", key=f"view_{order['id']}", use_container_width=True):
                    st.session_state.active_order_id = order["id"]
                    st.session_state.page = "my_orders"
                    st.rerun()
