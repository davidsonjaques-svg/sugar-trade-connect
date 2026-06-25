import streamlit as st
import time
from utils.ui import inject_global_css, brand_header, page_title, format_zar, require_login, status_badge
from utils.database import (get_order_by_id, create_payment, confirm_payment,
                             get_payment_by_order, update_order_status)

def render():
    inject_global_css()
    customer = require_login()

    brand_header()
    page_title("Payment", "Complete your payment to confirm your order")

    order_id = st.session_state.get("active_order_id")
    if not order_id:
        st.warning("No order selected. Please go to My Orders and select an order to pay.")
        if st.button("← Go to My Orders"):
            st.session_state.page = "my_orders"
            st.rerun()
        return

    order = get_order_by_id(order_id)
    if not order or order["customer_id"] != customer["id"]:
        st.error("Order not found.")
        return

    if order["status"] != "pending_payment":
        badge = status_badge(order["status"])
        st.markdown(f"""
        <div class="card card-success">
            <div style="font-size:16px; font-weight:700; color:#065F46;">Order Status: {badge}</div>
            <div style="margin-top:8px; color:#065F46;">
                Payment has already been processed for this order.
            </div>
        </div>
        """, unsafe_allow_html=True)
        col_a, _ = st.columns([1, 2])
        with col_a:
            if st.button("View Order Details →"):
                st.session_state.page = "my_orders"
                st.rerun()
        return

    # ── Order summary ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div class="card card-accent">
        <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
            <div>
                <div style="font-size:12px; color:#6B7280; text-transform:uppercase; letter-spacing:0.05em;">Order Reference</div>
                <div style="font-family:'Playfair Display',serif; font-size:22px; font-weight:700; color:#1B4332;">
                    {order['order_ref']}
                </div>
                <div style="font-size:14px; color:#4B5563; margin-top:4px;">
                    {order['product_type']} · {order['grade']} · {order['quantity_kg']:,.0f} kg
                </div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:12px; color:#6B7280;">Amount Due</div>
                <div style="font-family:'Playfair Display',serif; font-size:32px; font-weight:700; color:#1B4332;">
                    {format_zar(order['total_amount'])}
                </div>
                <div style="font-size:12px; color:#6B7280;">incl. VAT @ 15%</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card card-warning" style="margin-bottom:20px;">
        <strong>⚠️ Important:</strong> Goods will only be released once full payment is confirmed.
        Your order is reserved for 48 hours.
    </div>
    """, unsafe_allow_html=True)

    # ── Payment method tabs ───────────────────────────────────────────────────
    tab1, tab2 = st.tabs(["💳 Secure Online Payment", "📄 Upload Proof of Payment"])

    # ── TAB 1: Online payment gateway simulation ──────────────────────────────
    with tab1:
        st.markdown("""
        <div style="font-size:14px; color:#6B7280; margin-bottom:20px;">
            Pay securely using your credit/debit card or EFT through our encrypted payment gateway.
        </div>
        <div style="display:flex; gap:12px; margin-bottom:20px; flex-wrap:wrap;">
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Mastercard-logo.svg/1280px-Mastercard-logo.svg.png" height="28" style="object-fit:contain;" alt="Mastercard">
            <span style="font-size:24px; font-weight:700; color:#1A1FCE; font-family:sans-serif;">VISA</span>
            <span style="font-size:16px; font-weight:700; color:#1B4332; border:2px solid #1B4332; padding:2px 8px; border-radius:4px;">EFT</span>
        </div>
        """, unsafe_allow_html=True)

        with st.form("gateway_form"):
            st.markdown("#### Card Details")
            card_name = st.text_input("Cardholder Name", placeholder="As it appears on card")
            card_number = st.text_input("Card Number", placeholder="1234 5678 9012 3456", max_chars=19)
            col_exp, col_cvv = st.columns(2)
            with col_exp:
                expiry = st.text_input("Expiry Date", placeholder="MM/YY", max_chars=5)
            with col_cvv:
                cvv = st.text_input("CVV", placeholder="123", max_chars=4, type="password")

            st.markdown("""
            <div style="font-size:12px; color:#6B7280; margin-top:8px; display:flex; align-items:center; gap:6px;">
                🔒 Your payment is secured with 256-bit SSL encryption. We do not store card details.
            </div>
            """, unsafe_allow_html=True)

            pay_btn = st.form_submit_button(
                f"Pay {format_zar(order['total_amount'])} Now →",
                use_container_width=True
            )

        if pay_btn:
            errors = []
            if not card_name.strip(): errors.append("Cardholder name is required.")
            if len(card_number.replace(" ", "")) < 13: errors.append("Please enter a valid card number.")
            if not expiry or "/" not in expiry: errors.append("Please enter a valid expiry date (MM/YY).")
            if len(cvv) < 3: errors.append("Please enter a valid CVV.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                with st.spinner("Processing payment securely..."):
                    time.sleep(2.5)
                payment_id, payment_ref = create_payment(
                    order_id=order_id,
                    method="card_gateway",
                    amount=order["total_amount"],
                )
                confirm_payment(payment_id, notes=f"Approved via secure card gateway. Ref: {payment_ref}")
                st.session_state.payment_confirmed = True
                st.session_state.payment_ref = payment_ref
                st.rerun()

    # ── TAB 2: Upload proof of payment ────────────────────────────────────────
    with tab2:
        st.markdown("""
        <div style="font-size:14px; color:#6B7280; margin-bottom:20px;">
            Already made an EFT? Upload your bank-issued proof of payment below.
            Our AI verification system will analyse it instantly.
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="card">
            <div style="font-weight:700; font-size:14px; color:#1B4332; margin-bottom:12px;">Banking Details</div>
            <table style="font-size:14px; border-collapse:collapse; width:100%;">
                <tr><td style="color:#6B7280; padding:4px 0; width:160px;">Bank</td><td style="font-weight:600;">Standard Bank</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Account Name</td><td style="font-weight:600;">Sugar Trade Connect (Pty) Ltd</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Account Number</td><td style="font-weight:600;">012 345 678</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Branch Code</td><td style="font-weight:600;">051001</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Account Type</td><td style="font-weight:600;">Business Current</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Reference</td><td style="font-weight:700; color:#D4A017; font-size:16px;">{order['order_ref']}</td></tr>
                <tr><td style="color:#6B7280; padding:4px 0;">Amount</td><td style="font-weight:700; color:#1B4332; font-size:16px;">{format_zar(order['total_amount'])}</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload your Proof of Payment",
            type=["pdf", "jpg", "jpeg", "png"],
            help="Accepted: PDF, JPG, PNG. Max 10MB."
        )

        if uploaded_file:
            file_bytes = uploaded_file.read()
            mimetype = uploaded_file.type
            is_image = mimetype in ("image/jpeg", "image/png", "image/jpg")
            is_pdf = mimetype == "application/pdf"

            if is_image:
                st.image(file_bytes, caption="Uploaded Proof of Payment", use_container_width=True)

            st.markdown("#### 🤖 AI Verification Analysis")
            if st.button("Analyse Document with AI →", use_container_width=True):
                if is_image:
                    with st.spinner("Analysing your proof of payment with AI..."):
                        from utils.pop_verify import verify_pop_with_ai
                        result = verify_pop_with_ai(
                            image_data=file_bytes,
                            mimetype=mimetype,
                            expected_amount=order["total_amount"],
                            expected_ref=order["order_ref"],
                            beneficiary_hint="Sugar Trade"
                        )
                    _show_verification_result(result)
                    st.session_state[f"pop_result_{order_id}"] = result
                elif is_pdf:
                    st.info("📄 PDF uploaded. AI visual analysis works best with image files (JPG/PNG). "
                            "For PDFs, a manual review will be conducted within 2 business hours.")
                    st.session_state[f"pop_result_{order_id}"] = {"recommendation": "QUERY", "confidence_pct": 0}

            # Show cached result
            cached = st.session_state.get(f"pop_result_{order_id}")
            if cached:
                _show_verification_result(cached, show_title=False)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Submit Proof of Payment →", use_container_width=True):
                payment_id, payment_ref = create_payment(
                    order_id=order_id,
                    method="manual_pop",
                    amount=order["total_amount"],
                    pop_filename=uploaded_file.name,
                    pop_data=file_bytes,
                    pop_mimetype=mimetype,
                )
                # Auto-confirm if AI approved
                cached = st.session_state.get(f"pop_result_{order_id}", {})
                if cached.get("recommendation") == "APPROVE":
                    confirm_payment(payment_id, notes=f"AI verified. Confidence: {cached.get('confidence_pct')}%")
                    st.session_state.payment_confirmed = True
                else:
                    update_order_status(order_id, "pending_payment")
                st.session_state.payment_ref = payment_ref
                st.session_state.pop_submitted = True
                st.rerun()

    # ── Post-payment confirmation ─────────────────────────────────────────────
    if st.session_state.get("payment_confirmed"):
        st.session_state.payment_confirmed = False
        _show_payment_success(order, st.session_state.get("payment_ref", ""))

    if st.session_state.get("pop_submitted"):
        st.session_state.pop_submitted = False
        cached = st.session_state.get(f"pop_result_{order_id}", {})
        if cached.get("recommendation") == "APPROVE":
            _show_payment_success(order, st.session_state.get("payment_ref", ""))
        else:
            st.success("✅ Your proof of payment has been submitted and is under review. "
                       "You will be notified once confirmed (typically within 2 business hours).")


def _show_verification_result(result, show_title=True):
    if not result:
        return

    confidence = result.get("confidence_pct", 0)
    recommendation = result.get("recommendation", "QUERY")
    error = result.get("error")

    if show_title:
        st.markdown("#### 🤖 AI Verification Result")

    if error:
        st.warning(f"AI analysis could not be completed: {error}")
        return

    color_map = {"APPROVE": "#065F46", "QUERY": "#92400E", "REJECT": "#991B1B"}
    bg_map = {"APPROVE": "#D1FAE5", "QUERY": "#FEF3C7", "REJECT": "#FEE2E2"}
    icon_map = {"APPROVE": "✅", "QUERY": "⚠️", "REJECT": "❌"}

    col_conf, col_rec = st.columns(2)
    with col_conf:
        st.metric("AI Confidence", f"{confidence}%")
    with col_rec:
        st.markdown(f"""
        <div style='background:{bg_map.get(recommendation,"#F3F4F6")}; border-radius:10px; padding:12px; text-align:center;'>
            <div style='font-size:20px;'>{icon_map.get(recommendation,"❓")}</div>
            <div style='font-weight:700; color:{color_map.get(recommendation,"#374151")};'>{recommendation}</div>
        </div>
        """, unsafe_allow_html=True)

    if result.get("summary"):
        st.info(result["summary"])

    if result.get("extracted"):
        ext = result["extracted"]
        valid_ext = {k: v for k, v in ext.items() if v}
        if valid_ext:
            st.markdown("**Extracted from document:**")
            cols = st.columns(min(len(valid_ext), 3))
            for i, (k, v) in enumerate(valid_ext.items()):
                with cols[i % 3]:
                    st.markdown(f"""
                    <div style='background:#F8F6F1; border-radius:8px; padding:10px; font-size:13px;'>
                        <div style='color:#6B7280; text-transform:uppercase; font-size:11px;'>{k.replace('_',' ')}</div>
                        <div style='font-weight:600; margin-top:2px;'>{v}</div>
                    </div>
                    """, unsafe_allow_html=True)

    if result.get("red_flags"):
        for flag in result["red_flags"]:
            st.warning(f"🚩 {flag}")

    if result.get("findings"):
        with st.expander("View detailed findings"):
            for finding in result["findings"]:
                st.write(f"• {finding}")


def _show_payment_success(order, payment_ref):
    st.balloons()
    st.markdown(f"""
    <div class="card card-success" style="text-align:center; padding:40px;">
        <div style="font-size:56px; margin-bottom:16px;">🎉</div>
        <div style="font-family:'Playfair Display',serif; font-size:28px; font-weight:700; color:#065F46;">
            Payment Confirmed!
        </div>
        <div style="color:#065F46; font-size:16px; margin-top:12px;">
            Your order <strong>{order['order_ref']}</strong> is confirmed.
        </div>
        <div style="color:#6B7280; font-size:14px; margin-top:8px;">
            Payment Reference: <strong>{payment_ref}</strong>
        </div>
        <div style="color:#065F46; font-size:14px; margin-top:16px;">
            Your order is now being prepared for dispatch.
            You will receive shipment tracking updates shortly.
        </div>
    </div>
    """, unsafe_allow_html=True)
    col_a, col_b, _ = st.columns([1, 1, 2])
    with col_a:
        if st.button("View Order →"):
            st.session_state.page = "my_orders"
            st.rerun()
    with col_b:
        if st.button("Track Shipment →"):
            st.session_state.page = "track"
            st.rerun()
