#!/usr/bin/env python3
"""
Clear test data from database
"""

import os
import sys

# Add the current directory to the path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import db_manager
    print("✅ Successfully imported db_manager from app.py")
except ImportError as e:
    print(f"❌ Failed to import from app.py: {e}")
    sys.exit(1)

def clear_test_data():
    """Clear the test invoices we just created"""
    
    print("🧹 Clearing test data...")
    
    # Get current invoice count
    try:
        current_count_result = db_manager.execute_query("SELECT COUNT(*) as count FROM Invoices")
        current_count = current_count_result[0]['count'] if current_count_result else 0
        print(f"📊 Current invoice count: {current_count}")
        
        if current_count == 0:
            print("✅ Database is already empty")
            return
        
        # Show current invoices
        invoices = db_manager.execute_query("SELECT InvoiceID, InvoiceDate, Excl FROM Invoices ORDER BY rowid")
        print(f"📋 Current invoices:")
        for invoice in invoices:
            print(f"   • Invoice {invoice['InvoiceID']}: {invoice['InvoiceDate']} - €{invoice['Excl']}")
        
        # Clear all invoices
        deleted_count = db_manager.execute_update("DELETE FROM Invoices")
        print(f"🗑️  Deleted {deleted_count} invoices")
        
        # Verify
        final_count_result = db_manager.execute_query("SELECT COUNT(*) as count FROM Invoices")
        final_count = final_count_result[0]['count'] if final_count_result else 0
        print(f"📊 Final invoice count: {final_count}")
        
        if final_count == 0:
            print("✅ Database cleared successfully")
        else:
            print(f"⚠️  Warning: {final_count} invoices still remain")
            
    except Exception as e:
        print(f"❌ Error clearing data: {e}")

if __name__ == "__main__":
    clear_test_data()
