import sqlite3
import os
import hashlib
import secrets
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sugar_trade.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            company TEXT,
            phone TEXT,
            address TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_ref TEXT UNIQUE NOT NULL,
            customer_id INTEGER NOT NULL,
            product_type TEXT NOT NULL,
            grade TEXT NOT NULL,
            quantity_kg REAL NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            vat_rate REAL NOT NULL DEFAULT 0.15,
            vat_amount REAL NOT NULL,
            total_amount REAL NOT NULL,
            delivery_address TEXT NOT NULL,
            delivery_date TEXT,
            special_instructions TEXT,
            status TEXT DEFAULT 'pending_payment',
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (customer_id) REFERENCES customers(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            payment_ref TEXT UNIQUE NOT NULL,
            method TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            pop_filename TEXT,
            pop_data BLOB,
            pop_mimetype TEXT,
            verification_notes TEXT,
            verified_by TEXT,
            verified_at TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS shipments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            tracking_ref TEXT UNIQUE NOT NULL,
            carrier TEXT,
            status TEXT DEFAULT 'awaiting_dispatch',
            current_location TEXT,
            estimated_delivery TEXT,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (order_id) REFERENCES orders(id)
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS shipment_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shipment_id INTEGER NOT NULL,
            event_type TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT,
            timestamp TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (shipment_id) REFERENCES shipments(id)
        )
    """)

    conn.commit()
    conn.close()
    seed_demo_data()

def hash_password(password: str) -> str:
    salt = "sugar_trade_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

def seed_demo_data():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM customers")
    if c.fetchone()[0] == 0:
        c.execute("""
            INSERT INTO customers (email, password_hash, full_name, company, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, ("demo@sugarco.co.za", hash_password("demo123"), "Demo Customer",
              "Demo Trading (Pty) Ltd", "+27 82 555 1234", "123 Main Street, Johannesburg, 2001"))
        conn.commit()
    conn.close()

def get_customer_by_email(email: str):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM customers WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def create_customer(email, password, full_name, company, phone, address):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO customers (email, password_hash, full_name, company, phone, address)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (email, hash_password(password), full_name, company, phone, address))
        conn.commit()
        return True, "Account created successfully."
    except sqlite3.IntegrityError:
        return False, "An account with this email already exists."
    finally:
        conn.close()

def authenticate(email, password):
    customer = get_customer_by_email(email)
    if customer and customer["password_hash"] == hash_password(password):
        return customer
    return None

def generate_order_ref():
    return f"STC-{datetime.now().strftime('%Y%m%d')}-{secrets.token_hex(3).upper()}"

def generate_payment_ref():
    return f"PAY-{secrets.token_hex(5).upper()}"

def generate_tracking_ref():
    return f"TRK-{secrets.token_hex(5).upper()}"

def create_order(customer_id, product_type, grade, quantity_kg, unit_price,
                 delivery_address, delivery_date, special_instructions, vat_rate=0.15):
    subtotal = quantity_kg * unit_price
    vat_amount = subtotal * vat_rate
    total_amount = subtotal + vat_amount
    order_ref = generate_order_ref()

    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO orders (order_ref, customer_id, product_type, grade, quantity_kg,
            unit_price, subtotal, vat_rate, vat_amount, total_amount,
            delivery_address, delivery_date, special_instructions)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (order_ref, customer_id, product_type, grade, quantity_kg, unit_price,
          subtotal, vat_rate, vat_amount, total_amount,
          delivery_address, delivery_date, special_instructions))
    order_id = c.lastrowid
    conn.commit()
    conn.close()
    return order_id, order_ref

def get_orders_by_customer(customer_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE customer_id = ? ORDER BY created_at DESC", (customer_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_order_by_ref(order_ref):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE order_ref = ?", (order_ref,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_order_by_id(order_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def update_order_status(order_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()

def create_payment(order_id, method, amount, pop_filename=None, pop_data=None, pop_mimetype=None):
    payment_ref = generate_payment_ref()
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO payments (order_id, payment_ref, method, amount, status, pop_filename, pop_data, pop_mimetype)
        VALUES (?, ?, ?, ?, 'pending', ?, ?, ?)
    """, (order_id, payment_ref, method, amount, pop_filename, pop_data, pop_mimetype))
    payment_id = c.lastrowid
    conn.commit()
    conn.close()
    return payment_id, payment_ref

def get_payment_by_order(order_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM payments WHERE order_id = ? ORDER BY created_at DESC LIMIT 1", (order_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def confirm_payment(payment_id, notes=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        UPDATE payments SET status = 'confirmed', verification_notes = ?,
        verified_at = datetime('now') WHERE id = ?
    """, (notes, payment_id))
    c.execute("SELECT order_id FROM payments WHERE id = ?", (payment_id,))
    row = c.fetchone()
    if row:
        order_id = row["order_id"]
        c.execute("UPDATE orders SET status = 'payment_confirmed', updated_at = datetime('now') WHERE id = ?", (order_id,))
        tracking_ref = generate_tracking_ref()
        c.execute("""
            INSERT INTO shipments (order_id, tracking_ref, status, current_location)
            VALUES (?, ?, 'order_confirmed', 'Sugar Trade Distribution Centre, Durban')
        """, (order_id, tracking_ref))
        shipment_id = c.lastrowid
        c.execute("""
            INSERT INTO shipment_events (shipment_id, event_type, description, location)
            VALUES (?, 'order_confirmed', 'Order confirmed and payment verified. Preparing for dispatch.', 'Sugar Trade Distribution Centre, Durban')
        """, (shipment_id,))
    conn.commit()
    conn.close()

def get_shipment_by_order(order_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM shipments WHERE order_id = ? ORDER BY created_at DESC LIMIT 1", (order_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None

def get_shipment_events(shipment_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM shipment_events WHERE shipment_id = ? ORDER BY timestamp ASC", (shipment_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_shipment_event(shipment_id, event_type, description, location=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""
        INSERT INTO shipment_events (shipment_id, event_type, description, location)
        VALUES (?, ?, ?, ?)
    """, (shipment_id, event_type, description, location))
    c.execute("UPDATE shipments SET status = ?, current_location = ? WHERE id = ?",
              (event_type, location, shipment_id))
    conn.commit()
    conn.close()

def update_order_status_full(order_id, status):
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE orders SET status = ?, updated_at = datetime('now') WHERE id = ?", (status, order_id))
    conn.commit()
    conn.close()
