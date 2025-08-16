#!/usr/bin/env python3
"""
Test script to debug database initialization locally
"""

import os
import sys
import sqlite3
from pathlib import Path

# Set environment variables like in Docker
os.environ['DATABASE_PATH'] = 'data/ozark_finances.db'
os.environ['DATA_DIR'] = 'data'

# Create data directory
Path('data').mkdir(exist_ok=True)

# Test database creation
print(f"Creating database at: {os.environ['DATABASE_PATH']}")

try:
    conn = sqlite3.connect(os.environ['DATABASE_PATH'])
    cursor = conn.cursor()
    
    # Create Invoices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Invoices (
            InvoiceID TEXT PRIMARY KEY,
            InvoiceDate TEXT NOT NULL,
            Excl REAL NOT NULL,
            BTW REAL NOT NULL,
            Incl REAL NOT NULL,
            status TEXT DEFAULT 'active',
            deleted_at TEXT NULL,
            payment_status TEXT DEFAULT 'pending'
        )
    """)
    
    # Create other tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Withdraw (
            Date TEXT NOT NULL,
            Amount REAL NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS KwartaalData (
            tijdvak TEXT NOT NULL,
            betaling TEXT NOT NULL,
            kenmerk TEXT PRIMARY KEY,
            betaald TEXT NOT NULL,
            Amount REAL NOT NULL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DebtRegister (
            DebtName TEXT PRIMARY KEY,
            Amount REAL NOT NULL,
            UnixStamp INTEGER NOT NULL,
            OriginalDebt REAL NOT NULL
        )
    """)
    
    conn.commit()
    
    # Verify tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"✅ Tables created: {[t[0] for t in tables]}")
    
    # Test each table
    for table in ['Invoices', 'Withdraw', 'KwartaalData', 'DebtRegister']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"✅ Table {table}: {count} records")
    
    conn.close()
    
    print("✅ Database initialization successful!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
