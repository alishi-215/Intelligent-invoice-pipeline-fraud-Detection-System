import sqlite3
import os
from datetime import datetime

# Hamesha same invoices.db use karo — chahe kahan se bhi chalao
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "invoices.db")

def setup_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT,
            invoice_id TEXT,
            invoice_date TEXT,
            due_date TEXT,
            invoice_total REAL,
            status TEXT,
            processed_date TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_invoice(vendor, invoice_number, invoice_date, due_date, total, status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO invoices 
        (vendor_name, invoice_id, invoice_date, due_date, invoice_total, status, processed_date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (vendor, invoice_number, invoice_date, due_date, total, status,
          datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()
    print(f"Saved: {vendor} | {invoice_number} | {status}")

def find_invoice(vendor, invoice_number):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM invoices
        WHERE vendor_name = ? AND invoice_id = ?
    """, (vendor, invoice_number))
    result = cursor.fetchone()
    conn.close()
    return result

if __name__ == "__main__":
    print("Database ready!")