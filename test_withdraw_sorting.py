#!/usr/bin/env python3
"""
Test script for withdraw sorting functionality
"""

import os
import sys
import sqlite3
from datetime import datetime, timedelta
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def add_test_data():
    """Add some test withdraw data for sorting"""
    db_path = "ozark_finances.db"
    
    if not os.path.exists(db_path):
        print("Database file not found. Please run the app first to create the database.")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if Withdraw table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Withdraw'")
        if not cursor.fetchone():
            print("Withdraw table doesn't exist. Please create it first.")
            return False
        
        # Clear any existing test data
        cursor.execute("DELETE FROM Withdraw WHERE Description LIKE 'Test withdraw%'")
        
        # Generate test data with different dates and amounts
        test_data = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(10):
            date = base_date + timedelta(days=i*3)
            amount = round(random.uniform(10.50, 999.99), 2)
            description = f"Test withdraw {i+1}"
            
            # Format date as DD-MM-YYYY
            date_str = date.strftime("%d-%m-%Y")
            
            test_data.append((date_str, amount, description))
        
        # Insert test data
        cursor.executemany(
            "INSERT INTO Withdraw (Date, Amount, Description) VALUES (?, ?, ?)",
            test_data
        )
        
        conn.commit()
        print(f"✅ Added {len(test_data)} test withdraw entries for sorting")
        
        # Show sample data
        cursor.execute("SELECT Date, Amount, Description FROM Withdraw WHERE Description LIKE 'Test withdraw%' ORDER BY Date DESC LIMIT 5")
        results = cursor.fetchall()
        
        print("\n📋 Sample test data:")
        for row in results:
            print(f"   Date: {row[0]}, Amount: €{row[1]:.2f}, Description: {row[2]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error adding test data: {e}")
        return False

def test_sorting_query():
    """Test the sorting query directly"""
    db_path = "ozark_finances.db"
    
    if not os.path.exists(db_path):
        print("Database file not found.")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("\n🔍 Testing sorting queries:")
        
        # Test date sorting (ascending)
        print("\n📅 Date sorting (ascending):")
        cursor.execute("""
            SELECT Date, Amount, Description 
            FROM Withdraw 
            WHERE Description LIKE 'Test withdraw%'
            ORDER BY date(substr(Date, 7, 4) || '-' || substr(Date, 4, 2) || '-' || substr(Date, 1, 2)) ASC 
            LIMIT 3
        """)
        for row in cursor.fetchall():
            print(f"   {row[0]} | €{row[1]:.2f} | {row[2]}")
        
        # Test amount sorting (descending)
        print("\n💰 Amount sorting (descending):")
        cursor.execute("""
            SELECT Date, Amount, Description 
            FROM Withdraw 
            WHERE Description LIKE 'Test withdraw%'
            ORDER BY Amount DESC 
            LIMIT 3
        """)
        for row in cursor.fetchall():
            print(f"   {row[0]} | €{row[1]:.2f} | {row[2]}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error testing queries: {e}")

def main():
    """Main function"""
    print("🧪 Withdraw Sorting Test Script")
    print("=" * 40)
    
    if add_test_data():
        test_sorting_query()
        
        print("\n🚀 Test completed!")
        print("\nTo test the web interface:")
        print("1. Run: python app.py")
        print("2. Navigate to: http://localhost:5000/withdraws")
        print("3. Click on 'Date' and 'Amount' column headers to test sorting")
        print("4. Notice the sort indicators (arrows) and URL parameters")
        
        print("\n📝 What to look for:")
        print("- Clickable column headers with sort icons")
        print("- URL changes to include sort_by and sort_dir parameters")
        print("- Data sorted correctly by date or amount")
        print("- Pagination preserves sorting when changing pages")
        print("- Sort direction toggles on repeated clicks")

if __name__ == "__main__":
    main()
