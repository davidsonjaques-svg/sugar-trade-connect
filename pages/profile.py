import streamlit as st
import sqlite3
from utils.ui import inject_global_css, brand_header, page_title, format_zar, require_login
from utils.database import get_conn, hash_password, get_orders_by_customer

def render():
    inject_global_css()
    customer = require_login()

    brand_header()
    page_title("My Profile", "Manage your account details")

    col_info, col_stats = st.columns([1.5, 1])

    with col_info:
        with st.form("profile_form"):
            st.markdown("### Personal Details")
            full_name = st.text_input("Full Name", value=customer.get("full_name", ""))
            email = st.text_input("Email Address", value=customer.get("email", ""), disabled=True,
                                   help="Email cannot be changed. Contact support if needed.")
            company = st.text_input("Company Name", value=customer.get("company", "") or "")
            phone = st.text_input("Phone Number", value=customer.get("phone", "") or "")
            address = st.text_area("Default Delivery Address",
                                   value=customer.get("address", "") or "", height=90)

            st.markdown("---")
            st.markdown("### Change Password")
            st.caption("Leave blank to keep current password")
            new_password = st.text_input("New Password", type="password", placeholder="Leave blank to keep current")
            confirm_password = st.text_input("Confirm New Password", type="password")

            saved = st.form_submit_button("Save Changes →", use_container_width=True)

        if saved:
            errors = []
            if not full_name.strip(): errors.append("Full name cannot be empty.")
            if new_password and len(new_password) < 6: errors.append("Password must be at least 6 characters.")
            if new_password and new_password != confirm_password: errors.append("Passwords do not match.")

            if errors:
                for e in errors:
                    st.error(e)
            else:
                conn = get_conn()
                c = conn.cursor()
                if new_password:
                    c.execute("""
                        UPDATE customers SET full_name=?, company=?, phone=?, address=?, password_hash=?
                        WHERE id=?
                    """, (full_name.strip(), company.strip(), phone.strip(), address.strip(),
                          hash_password(new_password), customer["id"]))
                else:
                    c.execute("""
                        UPDATE customers SET full_name=?, company=?, phone=?, address=? WHERE id=?
                    """, (full_name.strip(), company.strip(), phone.strip(), address.strip(), customer["id"]))
                conn.commit()
                conn.close()

                # Refresh session
                from utils.database import get_customer_by_email
                st.session_state.customer = get_customer_by_email(customer["email"])
                st.success("Profile updated successfully.")

    with col_stats:
        st.markdown("### Account Summary")
        orders = get_orders_by_customer(customer["id"])
        total_orders = len(orders)
        total_value = sum(o["total_amount"] for o in orders)
        completed = sum(1 for o in orders if o["status"] == "delivered")
        total_kg = sum(o["quantity_kg"] for o in orders)

        st.markdown(f"""
        <div class="card card-accent" style="text-align:center;">
            <div style="font-size:12px; color:#6B7280; text-transform:uppercase; letter-spacing:0.05em;">Member Since</div>
            <div style="font-weight:700; font-size:16px; margin-top:4px;">{customer.get('created_at','')[:10]}</div>
        </div>
        """, unsafe_allow_html=True)

        st.metric("Total Orders Placed", total_orders)
        st.metric("Total Order Value", format_zar(total_value))
        st.metric("Orders Delivered", completed)
        st.metric("Total Sugar Ordered", f"{total_kg:,.0f} kg")

        st.markdown("""
        <div class="card" style="margin-top:16px;">
            <div style="font-weight:700; font-size:13px; color:#1B4332; margin-bottom:8px;">Support</div>
            <div style="font-size:13px; color:#4B5563;">
                📞 +27 31 000 0000<br>
                📧 support@sugartradeconnect.co.za<br>
                🕐 Mon–Fri, 8am–5pm SAST
            </div>
        </div>
        """, unsafe_allow_html=True)
