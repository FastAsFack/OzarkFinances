#!/usr/bin/env python3
"""
Test script to verify the download invoice fix.
"""

import sys
import os
import sqlite3

# Add the FlaskPort directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_row_object_access():
    """Test sqlite3.Row object access methods"""
    
    print("🧪 Testing sqlite3.Row Object Access")
    print("=" * 50)
    
    # Create a temporary in-memory database for testing
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Create a test table similar to Invoices
    cursor.execute("""
        CREATE TABLE test_invoices (
            InvoiceID TEXT,
            InvoiceDate TEXT,
            Excl REAL,
            BTW REAL,
            Incl REAL,
            payment_status TEXT
        )
    """)
    
    # Insert test data
    cursor.execute("""
        INSERT INTO test_invoices 
        (InvoiceID, InvoiceDate, Excl, BTW, Incl, payment_status)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('250022', '26-07-2025', 100.0, 21.0, 121.0, 'pending'))
    
    # Insert another record without payment_status (to test column missing scenario)
    cursor.execute("""
        ALTER TABLE test_invoices ADD COLUMN new_column TEXT
    """)
    
    # Test accessing the row
    cursor.execute("SELECT * FROM test_invoices WHERE InvoiceID = ?", ('250022',))
    row = cursor.fetchone()
    
    print(f"📊 Row type: {type(row)}")
    print(f"📊 Row keys: {list(row.keys())}")
    print(f"📊 Row values: {dict(row)}")
    
    # Test different access methods
    print(f"\n🔍 Testing access methods:")
    print(f"✅ Direct access: row['payment_status'] = {row['payment_status']}")
    
    try:
        # This should fail - Row objects don't have .get() method
        result = row.get('payment_status', 'default')
        print(f"❌ .get() method worked: {result}")
    except AttributeError as e:
        print(f"✅ .get() method failed as expected: {e}")
    
    # Test safe access method
    try:
        payment_status = row['payment_status'] if 'payment_status' in row.keys() else 'pending'
        print(f"✅ Safe access method: {payment_status}")
    except Exception as e:
        print(f"❌ Safe access failed: {e}")
    
    # Test accessing non-existent column
    try:
        non_existent = row['non_existent_column'] if 'non_existent_column' in row.keys() else 'default'
        print(f"✅ Non-existent column access: {non_existent}")
    except Exception as e:
        print(f"❌ Non-existent column access failed: {e}")
    
    conn.close()
    print(f"\n✅ sqlite3.Row access test completed!")

def test_invoice_download_logic():
    """Test the invoice download logic with the fix"""
    
    print(f"\n🧪 Testing Invoice Download Logic")
    print("=" * 50)
    
    # Simulate the fixed logic
    class MockRow:
        def __init__(self, data):
            self.data = data
            
        def __getitem__(self, key):
            return self.data[key]
            
        def keys(self):
            return self.data.keys()
    
    # Test with complete data
    invoice_with_status = MockRow({
        'InvoiceID': '250022',
        'InvoiceDate': '26-07-2025',
        'Excl': 100.0,
        'BTW': 21.0,
        'Incl': 121.0,
        'payment_status': 'paid'
    })
    
    # Test with missing payment_status
    invoice_without_status = MockRow({
        'InvoiceID': '250023',
        'InvoiceDate': '26-07-2025',
        'Excl': 200.0,
        'BTW': 42.0,
        'Incl': 242.0
    })
    
    for i, invoice in enumerate([invoice_with_status, invoice_without_status], 1):
        print(f"\n📋 Test Case {i}: Invoice {invoice['InvoiceID']}")
        
        # Apply the fixed logic
        try:
            payment_status = invoice['payment_status'] if 'payment_status' in invoice.keys() else 'pending'
            print(f"✅ Payment status: {payment_status}")
        except (KeyError, TypeError) as e:
            payment_status = 'pending'
            print(f"⚠️  Fallback to default: {payment_status} (Error: {e})")
        
        # Simulate Excel data population
        excel_data = {
            'A1': 'Invoice ID', 'B1': invoice['InvoiceID'],
            'A2': 'Date', 'B2': invoice['InvoiceDate'],
            'A3': 'Amount (Excl)', 'B3': invoice['Excl'],
            'A4': 'BTW', 'B4': invoice['BTW'],
            'A5': 'Amount (Incl)', 'B5': invoice['Incl'],
            'A6': 'Payment Status', 'B6': payment_status
        }
        
        print(f"📊 Excel data generated successfully:")
        for key, value in excel_data.items():
            if key.startswith('B'):
                print(f"   {excel_data[chr(ord(key[0]) - 1) + key[1:]]}: {value}")

if __name__ == "__main__":
    test_row_object_access()
    test_invoice_download_logic()
    print(f"\n🎯 All tests completed!")
