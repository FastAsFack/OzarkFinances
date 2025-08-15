"""
Quick test script to verify database connectivity
"""

import sqlite3
import os
from pathlib import Path

def test_db_connection():
    """Test database connection and basic operations"""
    
    # Try different possible database paths
    possible_paths = [
        '../data/FinanceData.sqlite',
        'data/FinanceData.sqlite',
        os.path.abspath('../data/FinanceData.sqlite'),
        os.path.abspath('data/FinanceData.sqlite')
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No database found. Creating new one...")
        # Create in the most likely location
        db_path = os.path.abspath('../data/FinanceData.sqlite')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # Create basic tables
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Invoices (
                InvoiceID TEXT PRIMARY KEY,
                InvoiceDate TEXT NOT NULL,
                Excl REAL NOT NULL,
                BTW REAL NOT NULL,
                Incl REAL NOT NULL
            )
        """)
        
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
        
        # Tables created successfully without sample data
        print("✅ Database tables created successfully!")
        
        conn.commit()
        conn.close()
        print(f"✅ Database created at: {db_path}")
    
    print(f"✅ Using database: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Test each table
        tables = ['Invoices', 'Withdraw', 'KwartaalData', 'DebtRegister']
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table}")
            count = cursor.fetchone()['count']
            print(f"✅ {table}: {count} records")
            
            # Show sample data
            cursor.execute(f"SELECT * FROM {table} LIMIT 2")
            rows = cursor.fetchall()
            for row in rows:
                print(f"   Sample: {dict(row)}")
        
        conn.close()
        print(f"\n✅ Database test successful!")
        print(f"Database location: {db_path}")
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("Database Connection Test")
    print("=" * 30)
    test_db_connection()
    input("\nPress Enter to exit...")
