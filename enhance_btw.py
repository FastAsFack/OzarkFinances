"""
Enhanced BTW Quarterly Payment System for Dutch VAT Management
Adds the BTW quarterly payment tracking functionality to the database
"""

import sqlite3
import os
from datetime import datetime, date

DATABASE_PATH = os.path.abspath('ozark_finances.db')

def enhance_btw_system():
    """Add BTW quarterly payment tracking table"""
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("Enhancing database for BTW quarterly payments...")
    
    # Create BTW Quarterly Payments table with your exact requirements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS btw_quarterly_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timeframe TEXT NOT NULL,
            quarter_months TEXT NOT NULL,
            latest_payment_date TEXT NOT NULL,
            payment_id TEXT,
            cost REAL NOT NULL,
            actual_payment_date TEXT,
            status TEXT DEFAULT 'pending',
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(timeframe)
        )
    """)
    print("✓ BTW Quarterly Payments table created/verified")
    
    # Add indexes for better performance
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_btw_timeframe 
        ON btw_quarterly_payments(timeframe)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_btw_status 
        ON btw_quarterly_payments(status)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_btw_payment_date 
        ON btw_quarterly_payments(latest_payment_date)
    """)
    
    print("✓ Database indexes created")
    
    # Create default quarters for current year if they don't exist
    current_year = datetime.now().year
    quarters = [
        (f"Q1 {current_year}", "Jan-Mar", f"{current_year}-04-30"),  # Due April 30th
        (f"Q2 {current_year}", "Apr-Jun", f"{current_year}-07-31"),  # Due July 31st
        (f"Q3 {current_year}", "Jul-Sep", f"{current_year}-10-31"),  # Due October 31st
        (f"Q4 {current_year}", "Oct-Dec", f"{current_year+1}-01-31") # Due January 31st next year
    ]
    
    for timeframe, months, due_date in quarters:
        cursor.execute("""
            INSERT OR IGNORE INTO btw_quarterly_payments 
            (timeframe, quarter_months, latest_payment_date, cost, status)
            VALUES (?, ?, ?, 0.0, 'pending')
        """, (timeframe, months, due_date))
    
    print(f"✓ Default quarters created for {current_year}")
    
    # Commit changes and close
    conn.commit()
    conn.close()
    
    print("BTW quarterly payment system enhancement completed!")

if __name__ == "__main__":
    print("Ozark Finances BTW System Enhancement")
    print("=" * 40)
    
    try:
        enhance_btw_system()
        print("\nEnhancement complete! BTW quarterly tracking is now available.")
        
    except Exception as e:
        print(f"\nError during enhancement: {e}")
        print("Please check the database path and permissions.")
        
    input("\nPress Enter to exit...")
