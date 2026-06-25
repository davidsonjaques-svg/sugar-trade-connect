import streamlit as st
from utils.ui import inject_global_css, brand_header, page_title, status_badge, format_zar, require_login
from utils.database import get_orders_by_customer, get_order_by_id, get_payment_by_order, get_shipment_by_order

def render():
    inject_global_css()
    customer = require_login()

    brand_header()

    # ── Post-order-placement confirmation banner ──────────────────────────────
    if st.session_state.get("just_placed_order"):
        st.session_state.just_placed_order = False
        st.success("✅ Your order has been received! Please proceed to payment to confirm your order.")

    orders = get_orders_by_customer(customer["id"])

    # ── If a specific order is selected, show detail ─────────────────────────
    active_id = st.session_state.get("active_order_id")
    if active_id:
        order = get_order_by_id(active_id)
        if order and order["customer_id"] == customer["id"]:
            _render_order_detail(order, customer)
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("← Back to All Orders"):
                st.session_state.active_order_id = None
                st.rerun()
            return

    # ── Order list ────────────────────────────────────────────────────────────
    page_title("My Orders", "View, pay, and manage all your orders")

    if not orders:
        st.markdown("""
        <div class="card" style="text-align:center; padding:48px;">
            <div style="font-size:48px;">📋</div>
            <div style="font-size:20px; font-weight:700; color:#1B4332; margin-top:16px;">No orders yet</div>
            <div style="color:#6B7280; margin-top:8px;">Place your first bulk sugar order to get started.</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Place Your First Order →"):
            st.session_state.page = "place_order"
            st.rerun()
        return

    # Filter bar
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        search = st.text_input("Search by order ref", placeholder="STC-...")
    with col_f2:
        status_filter = st.selectbox("Status", ["All", "Pending Payment", "Payment Confirmed",
                                                  "In Transit", "Delivered"])

    status_map = {
        "Pending Payment": "pending_payment",
        "Payment Confirmed": "payment_confirmed",
        "In Transit": "in_transit",
        "Delivered": "delivered",
    }

    filtered = orders
    if search:
        filtered = [o for o in filtered if search.upper() in o["order_ref"].upper()]
    if status_filter != "All":
        filtered = [o for o in filtered if o["status"] == status_map.get(status_filter, "")]

    for order in filtered:
        badge = status_badge(order["status"])
        payment = get_payment_by_order(order["id"])
        pay_status = payment["status"] if payment else "none"

        st.markdown(f"""
        <div class="card" style="border-left:4px solid {'#D4A017' if order['status']=='pending_payment' else '#40916C'};">
            <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:12px;">
                <div>
                    <div style="font-weight:700; font-size:17px; color:#1B4332;">{order['order_ref']}</div>
                    <div style="font-size:14px; color:#4B5563; margin-top:4px;">
                        {order['product_type']} &mdash; {order['grade']}
                    </div>
                    <div style="font-size:13px; color:#6B7280; margin-top:2px;">
                        {order['quantity_kg']:,.0f} kg &bull; {order['delivery_address'][:50]}...
                    </div>
                    <div style="font-size:12px; color:#9CA3AF; margin-top:4px;">Placed: {order['created_at'][:16]}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:22px; font-weight:700; color:#1B4332;">{format_zar(order['total_amount'])}</div>
                    <div style="margin-top:6px;">{badge}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_b, col_c, _ = st.columns([1, 1, 1, 2])
        with col_a:
            if st.button("View Details", key=f"detail_{order['id']}", use_container_width=True):
                st.session_state.active_order_id = order["id"]
                st.rerun()
        with col_b:
            if order["status"] == "pending_payment":
                if st.button("💳 Pay Now", key=f"pay_{order['id']}", use_container_width=True):
                    st.session_state.active_order_id = order["id"]
                    st.session_state.page = "payment"
                    st.rerun()
        with col_c:
            shipment = get_shipment_by_order(order["id"])
            if shipment:
                if st.button("🚚 Track", key=f"track_{order['id']}", use_container_width=True):
                    st.session_state.active_order_id = order["id"]
                    st.session_state.page = "track"
                    st.rerun()

def _render_order_detail(order, customer):
    status = order["status"]
    payment = get_payment_by_order(order["id"])
    shipment = get_shipment_by_order(order["id"])

    badge = status_badge(status)

    # ── Confirmation banner ───────────────────────────────────────────────────
    if status == "pending_payment":
        st.markdown("""
        <div class="card card-warning">
            <div style="font-size:18px; font-weight:700; color:#92400E;">⚠️ Payment Required</div>
            <div style="margin-top:8px; color:#92400E;">
                This order has been received and is <strong>reserved for 48 hours</strong>.
                Goods will <strong>NOT be released or dispatched</strong> until full payment is confirmed.
                Please proceed to payment to lock in your order.
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif status == "payment_confirmed":
        st.markdown("""
        <div class="card card-success">
            <div style="font-size:18px; font-weight:700; color:#065F46;">✅ Order Confirmed</div>
            <div style="margin-top:8px; color:#065F46;">
                Payment received and verified. Your order is confirmed and being prepared for dispatch.
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card card-accent">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div style="font-size:12px; color:#6B7280; text-transform:uppercase; letter-spacing:0.05em;">Order Reference</div>
                <div style="font-family:'Playfair Display',serif; font-size:26px; font-weight:700; color:#1B4332;">
                    {order['order_ref']}
                </div>
                <div style="margin-top:8px;">{badge}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:12px; color:#6B7280;">Order Date</div>
                <div style="font-weight:600;">{order['created_at'][:16]}</div>
                <div style="font-size:12px; color:#6B7280; margin-top:8px;">Requested Delivery</div>
                <div style="font-weight:600;">{order.get('delivery_date','TBC')}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="card">
            <div style="font-weight:700; font-size:14px; color:#1B4332; margin-bottom:12px; text-transform:uppercase; letter-spacing:0.05em;">Product Details</div>
            <table style="width:100%; font-size:14px; border-collapse:collapse;">
                <tr><td style="color:#6B7280; padding:4px 0;">Type</td><td style="font-weight:600; text-align:right;">{order['product_type']}</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Grade</td><td style="font-weight:600; text-align:right;">{order['grade']}</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Quantity</td><td style="font-weight:600; text-align:right;">{order['quantity_kg']:,.0f} kg</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Unit Price</td><td style="font-weight:600; text-align:right;">{format_zar(order['unit_price'])}/kg</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="card">
            <div style="font-weight:700; font-size:14px; color:#1B4332; margin-bottom:12px; text-transform:uppercase; letter-spacing:0.05em;">Pricing Summary</div>
            <table style="width:100%; font-size:14px; border-collapse:collapse;">
                <tr><td style="color:#6B7280; padding:4px 0;">Subtotal</td><td style="font-weight:600; text-align:right;">{format_zar(order['subtotal'])}</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">VAT ({int(order['vat_rate']*100)}%)</td><td style="font-weight:600; text-align:right;">{format_zar(order['vat_amount'])}</td></tr>
                <tr style="border-top:2px solid #E5E0D5;">
                    <td style="color:#1B4332; font-weight:700; padding:8px 0 0 0;">TOTAL DUE</td>
                    <td style="font-weight:700; font-size:18px; color:#1B4332; text-align:right; padding-top:8px;">{format_zar(order['total_amount'])}</td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="card">
        <div style="font-weight:700; font-size:14px; color:#1B4332; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.05em;">Delivery Address</div>
        <div style="color:#4B5563;">{order['delivery_address']}</div>
        {f'<div style="color:#6B7280; font-size:13px; margin-top:8px;">{order["special_instructions"]}</div>' if order.get("special_instructions") else ""}
    </div>
    """, unsafe_allow_html=True)

    # ── Customer details ─────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="card">
        <div style="font-weight:700; font-size:14px; color:#1B4332; margin-bottom:8px; text-transform:uppercase; letter-spacing:0.05em;">Buyer Details</div>
        <div style="font-size:14px; color:#4B5563;">
            <strong>{customer['full_name']}</strong>{f' &bull; {customer["company"]}' if customer.get("company") else ''}<br>
            {customer['email']} &bull; {customer.get('phone','')}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Action buttons ────────────────────────────────────────────────────────
    if status == "pending_payment":
        col_p, _ = st.columns([1, 2])
        with col_p:
            if st.button("💳 Proceed to Payment →", use_container_width=True):
                st.session_state.page = "payment"
                st.rerun()

    if shipment:
        col_t, _ = st.columns([1, 2])
        with col_t:
            if st.button("🚚 Track Shipment →", use_container_width=True):
                st.session_state.page = "track"
                st.rerun()
