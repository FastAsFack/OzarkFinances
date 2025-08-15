"""
Test the BTW Quarterly Payment System
"""

import sqlite3
import os
from datetime import datetime

DATABASE_PATH = os.path.abspath('ozark_finances.db')

def test_btw_system():
    """Test the BTW quarterly payment system"""
    
    print("Testing BTW Quarterly Payment System...")
    print("=" * 50)
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check if the table exists
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='btw_quarterly_payments'
    """)
    
    if cursor.fetchone():
        print("✓ BTW table exists")
    else:
        print("✗ BTW table does not exist")
        return
    
    # Check the data
    cursor.execute("SELECT * FROM btw_quarterly_payments ORDER BY timeframe")
    payments = cursor.fetchall()
    
    print(f"\nFound {len(payments)} BTW quarterly payments:")
    print("-" * 80)
    print(f"{'Timeframe':<12} {'Quarter':<10} {'Due Date':<12} {'Cost':<10} {'Status':<10}")
    print("-" * 80)
    
    for payment in payments:
        print(f"{payment['timeframe']:<12} {payment['quarter_months']:<10} "
              f"{payment['latest_payment_date']:<12} €{payment['cost']:<9.2f} {payment['status']:<10}")
    
    print("\n✓ BTW system test completed!")
    
    # Test invoice data for auto-calculation
    cursor.execute("SELECT COUNT(*) as count FROM Invoices WHERE status = 'active'")
    invoice_count = cursor.fetchone()['count']
    print(f"✓ Found {invoice_count} active invoices for auto-calculation")
    
    conn.close()

if __name__ == "__main__":
    test_btw_system()
    input("\nPress Enter to exit...")
