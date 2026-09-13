"""
database.py
------------
Single SQLite backend for the Anamalai Tiger Reserve Eco Shop app.
Covers: Product Master, Daily Sales Register, Cash Register,
Purchase Register, Stock Register, Bank Transaction Register.

All dates are stored internally as ISO strings 'YYYY-MM-DD' (sortable),
and displayed to the user as dd/mm/yyyy by the UI layer.
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecoshop.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = _connect()
    c = conn.cursor()

    # ---------------- Product Master ----------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS products (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL CHECK(category IN ('STOCK','GROCERY')),
            unit TEXT NOT NULL CHECK(unit IN ('Nos','Kg','Lt')),
            price REAL DEFAULT 0,
            current_stock REAL DEFAULT 0,
            created_on TEXT
        )
    """)

    # ---------------- Daily Sales Register ----------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS daily_sales (
            s_no INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            bill_from TEXT,
            bill_to TEXT,
            total_amount REAL DEFAULT 0,
            remarks TEXT
        )
    """)

    # ---------------- Cash Register (credit + debit) ----------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS cash_credit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            bill_from TEXT,
            bill_to TEXT,
            total_amount REAL DEFAULT 0
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS cash_debit (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            voucher_no TEXT,
            description TEXT,
            total_amount REAL DEFAULT 0
        )
    """)

    # ---------------- Purchase Register ----------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS purchase (
            s_no INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            purchase_bill_no TEXT,
            vendor_name TEXT,
            category TEXT CHECK(category IN ('STOCK','GROCERY')),
            item_code TEXT,
            item_name TEXT,
            quantity REAL,
            unit TEXT CHECK(unit IN ('Nos','Kg','Lt')),
            total_amount REAL DEFAULT 0,
            remarks TEXT,
            FOREIGN KEY(item_code) REFERENCES products(code)
        )
    """)

    # ---------------- Stock Register (day-wise snapshot) ----------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS stock_daywise (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            product_code TEXT NOT NULL,
            initial_stock REAL DEFAULT 0,
            sold_quantity REAL DEFAULT 0,
            balance_stock REAL DEFAULT 0,
            FOREIGN KEY(product_code) REFERENCES products(code),
            UNIQUE(date, product_code)
        )
    """)

    # ---------------- Bank Transaction Register ----------------
    c.execute("""
        CREATE TABLE IF NOT EXISTS bank_transactions (
            s_no INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            total_bills INTEGER DEFAULT 0,
            total_credited REAL DEFAULT 0,
            total_debited REAL DEFAULT 0,
            balance REAL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


# ============================================================
# PRODUCT MASTER
# ============================================================

def generate_product_code(category):
    """STOCK -> STK0001, GROCERY -> GRO0001, sequential per category."""
    prefix = "STK" if category == "STOCK" else "GRO"
    conn = _connect()
    row = conn.execute(
        "SELECT code FROM products WHERE category=? ORDER BY code DESC LIMIT 1",
        (category,)
    ).fetchone()
    conn.close()
    if row:
        last_num = int(row["code"][3:])
        new_num = last_num + 1
    else:
        new_num = 1
    return f"{prefix}{new_num:04d}"


def add_product(name, category, unit, price=0, opening_stock=0):
    code = generate_product_code(category)
    conn = _connect()
    conn.execute(
        "INSERT INTO products (code,name,category,unit,price,current_stock,created_on) "
        "VALUES (?,?,?,?,?,?,?)",
        (code, name, category, unit, price, opening_stock, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()
    return code


def get_products(category=None):
    conn = _connect()
    if category:
        rows = conn.execute("SELECT * FROM products WHERE category=? ORDER BY name", (category,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM products ORDER BY category, name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_stock(code, delta):
    """delta positive = stock added (purchase), negative = stock sold."""
    conn = _connect()
    conn.execute("UPDATE products SET current_stock = current_stock + ? WHERE code=?", (delta, code))
    conn.commit()
    conn.close()


# ============================================================
# DAILY SALES REGISTER
# ============================================================

def add_daily_sales(date_iso, bill_from, bill_to, total_amount, remarks=""):
    remarks = (remarks or "")[:150]
    conn = _connect()
    conn.execute(
        "INSERT INTO daily_sales (date,bill_from,bill_to,total_amount,remarks) VALUES (?,?,?,?,?)",
        (date_iso, bill_from, bill_to, total_amount, remarks)
    )
    conn.commit()
    conn.close()


def get_daily_sales(start_date=None, end_date=None):
    conn = _connect()
    if start_date and end_date:
        rows = conn.execute(
            "SELECT * FROM daily_sales WHERE date BETWEEN ? AND ? ORDER BY s_no", (start_date, end_date)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM daily_sales ORDER BY s_no").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# CASH REGISTER
# ============================================================

def add_cash_credit(date_iso, bill_from, bill_to, total_amount):
    conn = _connect()
    conn.execute(
        "INSERT INTO cash_credit (date,bill_from,bill_to,total_amount) VALUES (?,?,?,?)",
        (date_iso, bill_from, bill_to, total_amount)
    )
    conn.commit()
    conn.close()


def add_cash_debit(date_iso, voucher_no, description, total_amount):
    description = (description or "")[:150]
    conn = _connect()
    conn.execute(
        "INSERT INTO cash_debit (date,voucher_no,description,total_amount) VALUES (?,?,?,?)",
        (date_iso, voucher_no, description, total_amount)
    )
    conn.commit()
    conn.close()


def get_cash_register(start_date=None, end_date=None):
    conn = _connect()
    if start_date and end_date:
        credit = conn.execute(
            "SELECT * FROM cash_credit WHERE date BETWEEN ? AND ? ORDER BY date", (start_date, end_date)
        ).fetchall()
        debit = conn.execute(
            "SELECT * FROM cash_debit WHERE date BETWEEN ? AND ? ORDER BY date", (start_date, end_date)
        ).fetchall()
    else:
        credit = conn.execute("SELECT * FROM cash_credit ORDER BY date").fetchall()
        debit = conn.execute("SELECT * FROM cash_debit ORDER BY date").fetchall()
    conn.close()
    return [dict(r) for r in credit], [dict(r) for r in debit]


def get_monthly_abstract(year, month):
    """Returns day-wise credit/debit totals plus month-end closing figures."""
    start = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end = f"{year+1:04d}-01-01"
    else:
        end = f"{year:04d}-{month+1:02d}-01"

    conn = _connect()
    credit_rows = conn.execute(
        "SELECT date, SUM(total_amount) as total FROM cash_credit "
        "WHERE date >= ? AND date < ? GROUP BY date ORDER BY date",
        (start, end)
    ).fetchall()
    debit_rows = conn.execute(
        "SELECT date, SUM(total_amount) as total FROM cash_debit "
        "WHERE date >= ? AND date < ? GROUP BY date ORDER BY date",
        (start, end)
    ).fetchall()
    conn.close()

    daily = {}
    for r in credit_rows:
        daily.setdefault(r["date"], {"credit": 0, "debit": 0})["credit"] = r["total"]
    for r in debit_rows:
        daily.setdefault(r["date"], {"credit": 0, "debit": 0})["debit"] = r["total"]

    total_credit = sum(v["credit"] for v in daily.values())
    total_debit = sum(v["debit"] for v in daily.values())

    return {
        "daily": dict(sorted(daily.items())),
        "total_credit": total_credit,
        "total_debit": total_debit,
        "closing_balance": total_credit - total_debit,
    }


# ============================================================
# PURCHASE REGISTER
# ============================================================

def add_purchase(date_iso, purchase_bill_no, vendor_name, category, item_code,
                  item_name, quantity, unit, total_amount, remarks=""):
    remarks = (remarks or "")[:150]
    conn = _connect()
    conn.execute(
        "INSERT INTO purchase (date,purchase_bill_no,vendor_name,category,item_code,"
        "item_name,quantity,unit,total_amount,remarks) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (date_iso, purchase_bill_no, vendor_name, category, item_code,
         item_name, quantity, unit, total_amount, remarks)
    )
    conn.commit()
    conn.close()
    # Stock-category purchases increase current stock; groceries are consumables,
    # tracked in the purchase register only (per your spec).
    if category == "STOCK" and item_code:
        update_stock(item_code, quantity)


def get_purchases(category=None):
    conn = _connect()
    if category:
        rows = conn.execute("SELECT * FROM purchase WHERE category=? ORDER BY date", (category,)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM purchase ORDER BY date").fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ============================================================
# STOCK REGISTER
# ============================================================

def record_daily_stock_snapshot(date_iso):
    """
    Call once per day (e.g. on app open, or end-of-day close) to freeze
    that day's initial/sold/balance figures per product for day-wise history.
    """
    conn = _connect()
    products = conn.execute("SELECT * FROM products").fetchall()

    # Sold quantity today = sum of daily_sales-driven deductions.
    # Since sales aren't itemised in your Daily Sales Register (bill-range only),
    # sold_quantity here is tracked via any stock deductions you log manually
    # against a product for the date (see stock_manual_adjust below), plus
    # purchases (additions) already reflected in current_stock.
    for p in products:
        prev = conn.execute(
            "SELECT balance_stock FROM stock_daywise WHERE product_code=? AND date<? "
            "ORDER BY date DESC LIMIT 1",
            (p["code"], date_iso)
        ).fetchone()
        initial = prev["balance_stock"] if prev else p["current_stock"]
        balance = p["current_stock"]
        sold = max(initial - balance, 0)
        conn.execute(
            "INSERT OR REPLACE INTO stock_daywise (date,product_code,initial_stock,sold_quantity,balance_stock) "
            "VALUES (?,?,?,?,?)",
            (date_iso, p["code"], initial, sold, balance)
        )
    conn.commit()
    conn.close()


def stock_manual_adjust(product_code, qty_sold_or_used):
    """Use for point-of-sale deduction against a stock item (e.g. t-shirt sold)."""
    update_stock(product_code, -abs(qty_sold_or_used))


def get_current_stock():
    return get_products()


def get_daywise_stock(date_iso):
    conn = _connect()
    rows = conn.execute(
        "SELECT sd.*, p.name, p.unit FROM stock_daywise sd "
        "JOIN products p ON p.code = sd.product_code WHERE sd.date=? ORDER BY p.name",
        (date_iso,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_available_stock_dates():
    conn = _connect()
    rows = conn.execute("SELECT DISTINCT date FROM stock_daywise ORDER BY date").fetchall()
    conn.close()
    return [r["date"] for r in rows]


# ============================================================
# BANK TRANSACTION REGISTER
# ============================================================

def add_bank_transaction(date_iso, total_bills, total_credited, total_debited):
    conn = _connect()
    last = conn.execute("SELECT balance FROM bank_transactions ORDER BY s_no DESC LIMIT 1").fetchone()
    prev_balance = last["balance"] if last else 0
    balance = prev_balance + total_credited - total_debited
    conn.execute(
        "INSERT INTO bank_transactions (date,total_bills,total_credited,total_debited,balance) "
        "VALUES (?,?,?,?,?)",
        (date_iso, total_bills, total_credited, total_debited, balance)
    )
    conn.commit()
    conn.close()


def get_bank_transactions():
    conn = _connect()
    rows = conn.execute("SELECT * FROM bank_transactions ORDER BY s_no").fetchall()
    conn.close()
    return [dict(r) for r in rows]
