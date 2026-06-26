import streamlit as st
import time
from utils.ui import inject_global_css, brand_header, page_title, format_zar, require_login, status_badge
from utils.database import (get_orders_by_customer, get_order_by_id, get_shipment_by_order,
                             get_shipment_events, add_shipment_event, update_order_status_full)

SHIPMENT_STAGES = [
    ("order_confirmed",    "Order Confirmed",        "Payment verified, order locked in"),
    ("awaiting_dispatch",  "Awaiting Dispatch",       "Stock being allocated and prepared"),
    ("dispatched",         "Dispatched",              "Goods collected and handed to logistics"),
    ("in_transit",         "In Transit",              "Shipment en route to delivery address"),
    ("out_for_delivery",   "Out for Delivery",        "Vehicle loaded, delivery today"),
    ("delivered",          "Delivered",               "Goods received at destination"),
]

def render():
    inject_global_css()
    customer = require_login()

    brand_header()
    page_title("Track Shipment", "Real-time visibility on every order in transit")

    orders = get_orders_by_customer(customer["id"])
    trackable = [o for o in orders if o["status"] not in ("pending_payment", "cancelled")]

    if not trackable:
        st.markdown("""
        <div class="card" style="text-align:center; padding:48px;">
            <div style="font-size:48px;">🚚</div>
            <div style="font-size:20px; font-weight:700; color:#1B4332; margin-top:16px;">No Active Shipments</div>
            <div style="color:#6B7280; margin-top:8px;">
                Once your payment is confirmed, shipment tracking will appear here.
            </div>
        </div>
        """, unsafe_allow_html=True)
        return

    # Order selector
    active_id = st.session_state.get("active_order_id")
    order_options = {f"{o['order_ref']} — {format_zar(o['total_amount'])}": o["id"] for o in trackable}

    default_key = next((k for k, v in order_options.items() if v == active_id), list(order_options.keys())[0])
    selected_label = st.selectbox("Select Order", list(order_options.keys()),
                                   index=list(order_options.keys()).index(default_key))
    selected_order_id = order_options[selected_label]
    st.session_state.active_order_id = selected_order_id

    order = get_order_by_id(selected_order_id)
    shipment = get_shipment_by_order(selected_order_id)

    if not shipment:
        st.info("Shipment details will appear here once payment is confirmed and order is processed.")
        return

    events = get_shipment_events(shipment["id"])
    current_status = shipment["status"]

    # ── Tracking header ───────────────────────────────────────────────────────
    stage_keys = [s[0] for s in SHIPMENT_STAGES]
    current_idx = stage_keys.index(current_status) if current_status in stage_keys else 0

    progress_pct = int((current_idx / (len(SHIPMENT_STAGES) - 1)) * 100)

    st.markdown(f"""
    <div class="card card-accent">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; margin-bottom:16px;">
            <div>
                <div style="font-size:12px; color:#6B7280; text-transform:uppercase; letter-spacing:0.05em;">Tracking Reference</div>
                <div style="font-family:'Playfair Display',serif; font-size:22px; font-weight:700; color:#1B4332;">
                    {shipment['tracking_ref']}
                </div>
            </div>
            <div style="text-align:right;">
                {status_badge(current_status)}
                <div style="font-size:12px; color:#6B7280; margin-top:6px;">
                    📍 {shipment.get('current_location','Unknown')}
                </div>
            </div>
        </div>
        <div style="background:#E5E0D5; border-radius:4px; height:8px; margin-bottom:8px;">
            <div style="background:linear-gradient(90deg,#1B4332,#40916C); height:8px; border-radius:4px;
                        width:{progress_pct}%; transition:width 0.5s;"></div>
        </div>
        <div style="display:flex; justify-content:space-between; font-size:11px; color:#6B7280;">
            <span>Order Confirmed</span>
            <span>In Transit</span>
            <span>Delivered</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Stage pills ───────────────────────────────────────────────────────────
    st.markdown("#### Shipment Progress")
    stage_cols = st.columns(len(SHIPMENT_STAGES))
    for i, (key, label, _) in enumerate(SHIPMENT_STAGES):
        with stage_cols[i]:
            done = i <= current_idx
            active = i == current_idx
            bg = "#1B4332" if done else "#E5E0D5"
            fg = "#ffffff" if done else "#9CA3AF"
            ring = "border:2px solid #D4A017;" if active else ""
            st.markdown(f"""
            <div style="background:{bg}; color:{fg}; border-radius:10px; padding:10px 6px;
                        text-align:center; font-size:11px; font-weight:600; {ring}
                        transition:all 0.3s;">
                {'✓' if done and not active else ('●' if active else '○')}
                <div style="margin-top:4px;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    col_timeline, col_details = st.columns([1.4, 1])

    with col_timeline:
        st.markdown("#### Event Timeline")
        if events:
            st.markdown('<div class="timeline">', unsafe_allow_html=True)
            for i, event in enumerate(reversed(events)):
                is_latest = i == 0
                dot_class = "active" if is_latest else ""
                st.markdown(f"""
                <div class="timeline-item">
                    <div class="timeline-dot {dot_class}"></div>
                    <div class="timeline-time">{event['timestamp'][:16]}</div>
                    <div class="timeline-title">{event['event_type'].replace('_',' ').title()}</div>
                    <div class="timeline-desc">{event['description']}</div>
                    {f'<div class="timeline-desc">📍 {event["location"]}</div>' if event.get("location") else ''}
                </div>
                """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No events recorded yet.")

    with col_details:
        st.markdown("#### Order Summary")
        est_delivery = shipment.get("estimated_delivery", "To be confirmed")
        st.markdown(f"""
        <div class="card">
            <table style="font-size:13px; width:100%; border-collapse:collapse;">
                <tr><td style="color:#6B7280; padding:4px 0;">Order Ref</td><td style="font-weight:600; text-align:right;">{order['order_ref']}</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Product</td><td style="font-weight:600; text-align:right;">{order['product_type']}</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Quantity</td><td style="font-weight:600; text-align:right;">{order['quantity_kg']:,.0f} kg</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Delivery To</td><td style="font-weight:600; text-align:right; font-size:12px;">{order['delivery_address'][:40]}...</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Requested</td><td style="font-weight:600; text-align:right;">{order.get('delivery_date','TBC')}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        # ── Advance shipment (for demo purposes) ──────────────────────────────
        if current_status != "delivered":
            st.markdown("#### 🔧 Advance Status (Demo)")
            st.caption("Simulate shipment progression for demonstration")
            next_idx = current_idx + 1
            if next_idx < len(SHIPMENT_STAGES):
                next_key, next_label, next_desc = SHIPMENT_STAGES[next_idx]
                location_map = {
                    "awaiting_dispatch": "Sugar Trade Distribution Centre, Durban",
                    "dispatched": "Durban Logistics Hub",
                    "in_transit": "N3 Highway, En Route",
                    "out_for_delivery": "Local Delivery Vehicle",
                    "delivered": order["delivery_address"],
                }
                if st.button(f"Advance → {next_label}", use_container_width=True):
                    add_shipment_event(
                        shipment_id=shipment["id"],
                        event_type=next_key,
                        description=next_desc,
                        location=location_map.get(next_key, "")
                    )
                    if next_key == "delivered":
                        update_order_status_full(order["id"], "delivered")
                    st.rerun()

        # ── Contact ───────────────────────────────────────────────────────────
        st.markdown("""
        <div class="card" style="margin-top:12px;">
            <div style="font-weight:700; font-size:13px; color:#1B4332; margin-bottom:8px;">Need Help?</div>
            <div style="font-size:13px; color:#4B5563;">
                📞 +27 31 000 0000<br>
                📧 logistics@sugartradeconnect.co.za<br>
                🕐 Mon–Fri, 7am–5pm SAST
            </div>
        </div>
        """, unsafe_allow_html=True)
