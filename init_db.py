"""
Database initialization script for Ozark Finances Flask Port
This script creates the necessary SQLite tables if they don't exist.
"""

import sqlite3
import os
from pathlib import Path

# Database path (adjust as needed)
DATABASE_PATH = os.path.abspath('ozark_finances.db')
DATA_DIR = Path(os.path.dirname(DATABASE_PATH))

def init_database():
    """Initialize the database with required tables"""
    
    # Create data directory if it doesn't exist (not needed for current directory)
    # DATA_DIR.mkdir(exist_ok=True)
    
    # Connect to database
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print(f"Initializing database at: {DATABASE_PATH}")
    
    # Create Invoices table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Invoices (
            InvoiceID TEXT PRIMARY KEY,
            InvoiceDate TEXT NOT NULL,
            Excl REAL NOT NULL,
            BTW REAL NOT NULL,
            Incl REAL NOT NULL,
            status TEXT DEFAULT 'active',
            deleted_at TEXT NULL
        )
    """)
    
    # Add status and deleted_at columns to existing table if they don't exist
    try:
        cursor.execute("ALTER TABLE Invoices ADD COLUMN status TEXT DEFAULT 'active'")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE Invoices ADD COLUMN deleted_at TEXT NULL")
    except sqlite3.OperationalError:
        pass  # Column already exists
    
    try:
        cursor.execute("ALTER TABLE Invoices ADD COLUMN payment_status TEXT DEFAULT 'pending'")
    except sqlite3.OperationalError:
        pass  # Column already exists
    print("✓ Invoices table created/verified")
    
    # Create Withdraw table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Withdraw (
            Date TEXT NOT NULL,
            Amount REAL NOT NULL
        )
    """)
    print("✓ Withdraw table created/verified")
    
    # Create KwartaalData table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS KwartaalData (
            tijdvak TEXT NOT NULL,
            betaling TEXT NOT NULL,
            kenmerk TEXT PRIMARY KEY,
            betaald TEXT NOT NULL,
            Amount REAL NOT NULL
        )
    """)
    print("✓ KwartaalData table created/verified")
    
    # Create DebtRegister table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS DebtRegister (
            DebtName TEXT PRIMARY KEY,
            Amount REAL NOT NULL,
            UnixStamp INTEGER NOT NULL,
            OriginalDebt REAL NOT NULL
        )
    """)
    print("✓ DebtRegister table created/verified")
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("\nDatabase initialization completed successfully!")
    print(f"Database location: {os.path.abspath(DATABASE_PATH)}")

def add_sample_data():
    """Add some sample data for testing"""
    print("\nSample data functionality has been removed.")
    print("✓ Database is ready for fresh data!")
    return

if __name__ == "__main__":
    print("Ozark Finances Database Initialization")
    print("=" * 40)
    
    try:
        init_database()
        
        # Ask if user wants sample data
        response = input("\nWould you like to add sample data for testing? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            add_sample_data()
        
        print("\nSetup complete! You can now run the Flask application with:")
        print("python app.py")
        
    except Exception as e:
        print(f"\nError during initialization: {e}")
        print("Please check the database path and permissions.")
        
    input("\nPress Enter to exit...")
