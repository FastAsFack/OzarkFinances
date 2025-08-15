"""
Clear all data from the Ozark Finances database
This script removes all existing data and leaves you with empty tables
"""

import sqlite3
import os
from pathlib import Path

def clear_all_data():
    """Clear all data from all tables"""
    
    # Try different possible database paths
    possible_paths = [
        '../data/FinanceData.sqlite',
        'data/FinanceData.sqlite',
        'FinanceData.sqlite',
        os.path.abspath('../data/FinanceData.sqlite'),
        os.path.abspath('data/FinanceData.sqlite')
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ No database found. Nothing to clear.")
        return
    
    print(f"🗑️  Found database: {db_path}")
    
    # Confirm with user
    confirm = input("⚠️  Are you sure you want to DELETE ALL DATA? (type 'DELETE' to confirm): ")
    if confirm != 'DELETE':
        print("❌ Operation cancelled.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Clear all tables
        tables = ['Invoices', 'Withdraw', 'KwartaalData', 'DebtRegister']
        
        for table in tables:
            try:
                cursor.execute(f"DELETE FROM {table}")
                count = cursor.rowcount
                print(f"✅ Cleared {count} records from {table}")
            except sqlite3.Error as e:
                print(f"⚠️  Could not clear {table}: {e}")
        
        conn.commit()
        conn.close()
        
        print("\n🎉 All data has been cleared successfully!")
        print("Your database is now fresh and ready for new data.")
        
    except Exception as e:
        print(f"❌ Error clearing database: {e}")

if __name__ == "__main__":
    print("Ozark Finances - Database Clear Utility")
    print("=" * 40)
    clear_all_data()
