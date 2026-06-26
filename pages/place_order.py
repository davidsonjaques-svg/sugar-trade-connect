import streamlit as st
from datetime import date, timedelta
from utils.ui import inject_global_css, brand_header, page_title, format_zar, require_login
from utils.database import create_order

PRODUCTS = {
    "White Sugar": {
        "grades": ["Superior Grade A", "Grade B Standard", "Industrial Grade"],
        "price_per_kg": {"Superior Grade A": 18.50, "Grade B Standard": 16.00, "Industrial Grade": 13.50},
        "description": "Refined white sugar, HACCP certified"
    },
    "Raw Sugar": {
        "grades": ["ICUMSA 600", "ICUMSA 1200", "Mill White"],
        "price_per_kg": {"ICUMSA 600": 14.00, "ICUMSA 1200": 12.50, "Mill White": 11.00},
        "description": "Raw cane sugar direct from mill"
    },
    "Brown Sugar": {
        "grades": ["Light Brown", "Dark Brown", "Demerara"],
        "price_per_kg": {"Light Brown": 17.00, "Dark Brown": 17.50, "Demerara": 19.00},
        "description": "Soft brown sugar with natural molasses"
    },
    "Speciality Sugar": {
        "grades": ["Castor Sugar", "Icing Sugar", "Coffee Crystals"],
        "price_per_kg": {"Castor Sugar": 22.00, "Icing Sugar": 24.00, "Coffee Crystals": 21.00},
        "description": "Premium speciality sugars for food service"
    },
}

PACKAGING = ["25 kg Bags", "50 kg Bags", "1 Tonne Bulk Bags (IBC)", "Loose Bulk (Tanker)"]
INCOTERMS = ["EXW (Ex Works)", "DDP (Delivered Duty Paid)", "DAP (Delivered at Place)", "CPT (Carriage Paid To)"]
VAT_RATE = 0.15
PLATFORM_FEE_RATE = 0.015   # 1.5% — your revenue on every order
GATEWAY_FEE_RATE  = 0.029   # 2.9% — PayFast/Peach standard rate (absorbed, shown transparently)

def render():
    inject_global_css()
    customer = require_login()

    brand_header()
    page_title("Place New Order", "Complete the form below to submit your bulk sugar order")

    with st.form("order_form"):
        # ── Product selection ────────────────────────────────────────────────
        st.markdown("### 🌾 Product Details")
        col1, col2 = st.columns(2)
        with col1:
            product_type = st.selectbox("Sugar Type *", list(PRODUCTS.keys()))
        with col2:
            grades = PRODUCTS[product_type]["grades"]
            grade = st.selectbox("Grade / Quality *", grades)

        prices = PRODUCTS[product_type]["price_per_kg"]
        unit_price = prices[grade]

        col3, col4 = st.columns(2)
        with col3:
            quantity_kg = st.number_input(
                "Quantity (kg) *",
                min_value=500.0, max_value=1_000_000.0,
                value=1000.0, step=500.0,
                help="Minimum order: 500 kg"
            )
        with col4:
            packaging = st.selectbox("Packaging *", PACKAGING)

        # ── Live fee calculation ──────────────────────────────────────────────
        subtotal          = quantity_kg * unit_price
        platform_fee      = subtotal * PLATFORM_FEE_RATE
        subtotal_after    = subtotal + platform_fee
        vat_amt           = subtotal_after * VAT_RATE
        total             = subtotal_after + vat_amt
        gateway_fee       = total * GATEWAY_FEE_RATE
        net_to_trader     = total - gateway_fee

        st.markdown(f"""
        <div class="card card-accent" style="margin-top:12px;">
            <div style="font-weight:700; font-size:13px; color:#1B4332; text-transform:uppercase;
                        letter-spacing:0.05em; margin-bottom:16px;">📊 Live Order Pricing</div>
            <table style="width:100%; font-size:14px; border-collapse:collapse;">
                <tr>
                    <td style="color:#6B7280; padding:6px 0;">
                        Product Subtotal
                        <span style="font-size:11px; color:#9CA3AF;">({quantity_kg:,.0f} kg × {format_zar(unit_price)}/kg)</span>
                    </td>
                    <td style="font-weight:600; text-align:right;">{format_zar(subtotal)}</td>
                </tr>
                <tr>
                    <td style="color:#6B7280; padding:6px 0;">
                        Platform Fee
                        <span style="font-size:11px; color:#9CA3AF;">({int(PLATFORM_FEE_RATE*100)}% — trading platform charge)</span>
                    </td>
                    <td style="font-weight:600; text-align:right; color:#D4A017;">{format_zar(platform_fee)}</td>
                </tr>
                <tr style="border-top:1px solid #E5E0D5;">
                    <td style="color:#6B7280; padding:6px 0;">Subtotal before VAT</td>
                    <td style="font-weight:600; text-align:right;">{format_zar(subtotal_after)}</td>
                </tr>
                <tr>
                    <td style="color:#6B7280; padding:6px 0;">
                        VAT
                        <span style="font-size:11px; color:#9CA3AF;">({int(VAT_RATE*100)}% — South African standard rate)</span>
                    </td>
                    <td style="font-weight:600; text-align:right; color:#D4A017;">{format_zar(vat_amt)}</td>
                </tr>
                <tr style="border-top:2px solid #1B4332;">
                    <td style="font-weight:700; font-size:16px; color:#1B4332; padding:10px 0 6px 0;">
                        TOTAL DUE
                    </td>
                    <td style="font-weight:700; font-size:22px; color:#1B4332; text-align:right; padding-top:10px;">
                        {format_zar(total)}
                    </td>
                </tr>
                <tr style="border-top:1px dashed #E5E0D5;">
                    <td style="color:#9CA3AF; font-size:12px; padding:8px 0 2px 0;">
                        Payment Gateway Fee (est. {int(GATEWAY_FEE_RATE*100)}% — absorbed by platform)
                    </td>
                    <td style="color:#9CA3AF; font-size:12px; text-align:right; padding-top:8px;">
                        ({format_zar(gateway_fee)})
                    </td>
                </tr>
                <tr>
                    <td style="color:#6B7280; font-size:12px; padding:2px 0;">Net settlement to Sugar Trade Connect</td>
                    <td style="color:#1B4332; font-size:13px; font-weight:700; text-align:right;">
                        {format_zar(net_to_trader)}
                    </td>
                </tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Delivery details ─────────────────────────────────────────────────
        st.markdown("### 🚚 Delivery Details")
        delivery_address = st.text_area(
            "Drop-off / Delivery Address *",
            value=customer.get("address", ""),
            placeholder="Street address, City, Province, Postal Code",
            height=90
        )

        col5, col6 = st.columns(2)
        with col5:
            min_date = date.today() + timedelta(days=3)
            delivery_date = st.date_input(
                "Requested Delivery Date *",
                value=min_date,
                min_value=min_date,
                help="Minimum 3 business days from today"
            )
        with col6:
            incoterm = st.selectbox("Delivery Terms (Incoterms) *", INCOTERMS)

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Order & compliance ───────────────────────────────────────────────
        st.markdown("### 📋 Order & Compliance")
        col7, col8 = st.columns(2)
        with col7:
            po_number = st.text_input("Your PO Number (optional)", placeholder="PO-2024-001")
        with col8:
            contact_person = st.text_input("Site Contact Person *", placeholder="Name of person receiving goods")

        contact_phone = st.text_input("Site Contact Number *", placeholder="+27 82 000 0000")
        special_instructions = st.text_area(
            "Special Instructions / Notes",
            placeholder="e.g. Delivery must be before 10am, forklift available on site, etc.",
            height=80
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Terms ────────────────────────────────────────────────────────────
        st.markdown("### ⚖️ Terms & Conditions")
        st.markdown(f"""
        <div style='background:#f8f6f1; border-radius:8px; padding:16px; font-size:13px; color:#4B5563;
                    border:1px solid #E5E0D5; margin-bottom:12px;'>
        By placing this order you agree to the following:<br><br>
        • Orders are subject to stock availability and will be confirmed upon payment receipt.<br>
        • <strong>Goods will NOT be released or dispatched until full payment is confirmed.</strong><br>
        • Payment must be received within 48 hours of order placement or the order will lapse.<br>
        • VAT is charged at the current South African standard rate of 15%.<br>
        • Delivery dates are estimates and may vary by ± 1 business day.<br>
        • Sugar Trade Connect reserves the right to cancel orders in the event of pricing errors.
        </div>
        """, unsafe_allow_html=True)

        agree = st.checkbox("I agree to the terms and conditions above *")

        submitted = st.form_submit_button("Submit Order →", use_container_width=True)

    if submitted:
        errors = []
        if not delivery_address.strip(): errors.append("Delivery address is required.")
        if not contact_person.strip(): errors.append("Site contact person is required.")
        if not contact_phone.strip(): errors.append("Site contact number is required.")
        if not agree: errors.append("You must agree to the terms and conditions.")

        if errors:
            for e in errors:
                st.error(e)
        else:
            extra = f"Packaging: {packaging} | Incoterms: {incoterm} | Contact: {contact_person} ({contact_phone})"
            if po_number: extra += f" | PO: {po_number}"
            if special_instructions: extra += f" | Notes: {special_instructions}"

            order_id, order_ref = create_order(
                customer_id=customer["id"],
                product_type=product_type,
                grade=grade,
                quantity_kg=quantity_kg,
                unit_price=unit_price,
                delivery_address=delivery_address.strip(),
                delivery_date=str(delivery_date),
                special_instructions=extra,
                vat_rate=VAT_RATE,
                platform_fee_rate=PLATFORM_FEE_RATE,
                gateway_fee_rate=GATEWAY_FEE_RATE,
            )

            st.session_state.active_order_id = order_id
            st.session_state.just_placed_order = True
            st.session_state.page = "my_orders"
            st.rerun()
