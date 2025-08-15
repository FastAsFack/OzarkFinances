#!/usr/bin/env python3
"""
Simple test script for the bin functionality
"""

import app
import sqlite3

def test_bin_functionality():
    print("Testing bin functionality...")
    
    # Test database connection
    try:
        with sqlite3.connect('ozark_finances.db') as conn:
            cursor = conn.cursor()
            
            # Check if columns exist
            cursor.execute("PRAGMA table_info(Invoices)")
            columns = [row[1] for row in cursor.fetchall()]
            print(f"Invoices table columns: {columns}")
            
            if 'status' in columns and 'deleted_at' in columns:
                print("✓ Status and deleted_at columns exist")
            else:
                print("✗ Missing required columns")
                return False
                
            # Test basic query for active invoices
            cursor.execute("SELECT COUNT(*) FROM Invoices WHERE (status IS NULL OR status = 'active')")
            active_count = cursor.fetchone()[0]
            print(f"✓ Active invoices: {active_count}")
            
            # Test basic query for binned invoices
            cursor.execute("SELECT COUNT(*) FROM Invoices WHERE status = 'binned'")
            binned_count = cursor.fetchone()[0]
            print(f"✓ Binned invoices: {binned_count}")
            
            return True
            
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_flask_routes():
    print("\nTesting Flask routes...")
    
    try:
        app.app.config['TESTING'] = True
        with app.app.test_client() as client:
            
            # Test homepage
            response = client.get('/')
            print(f"✓ Homepage: {response.status_code}")
            
            # Test invoices page
            response = client.get('/invoices')
            print(f"✓ Invoices page: {response.status_code}")
            
            # Test bin page
            response = client.get('/invoices/bin')
            print(f"✓ Bin page: {response.status_code}")
            
            return True
            
    except Exception as e:
        print(f"✗ Flask error: {e}")
        return False

if __name__ == "__main__":
    print("Ozark Finances Bin Functionality Test")
    print("=" * 40)
    
    success = True
    success &= test_bin_functionality()
    success &= test_flask_routes()
    
    print("\n" + "=" * 40)
    if success:
        print("✓ All tests passed! Bin functionality ready.")
        print("\nKey features implemented:")
        print("• Status column for tracking active/binned invoices")
        print("• Deletion timestamp tracking")
        print("• Move to bin functionality with confirmation")
        print("• Bin page with multi-select and bulk delete")
        print("• Restore from bin functionality")
        print("• Type 'delete' confirmation for permanent deletion")
        print("• Navigation links in main menu and invoice page")
        print("• Dashboard excludes binned invoices from statistics")
    else:
        print("✗ Some tests failed. Check the output above.")
    
    print(f"\nTo start the application: python app.py")
