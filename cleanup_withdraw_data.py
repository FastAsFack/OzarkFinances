#!/usr/bin/env python3
"""
Database cleanup: Fix any string amounts in Withdraw table
"""

import sqlite3
import os

def clean_withdraw_amounts(db_path):
    """Clean up any invalid amount data in Withdraw table"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all withdraw records
        cursor.execute("SELECT rowid, Date, Amount, Description FROM Withdraw")
        records = cursor.fetchall()
        
        fixed_count = 0
        deleted_count = 0
        
        for rowid, date, amount, description in records:
            try:
                # Try to convert to float
                if isinstance(amount, str):
                    # Try to clean up the string and convert
                    cleaned_amount = amount.replace(',', '.').strip()
                    float_amount = float(cleaned_amount)
                    
                    # Update the record with the float value
                    cursor.execute("UPDATE Withdraw SET Amount = ? WHERE rowid = ?", (float_amount, rowid))
                    fixed_count += 1
                    print(f"Fixed amount for record {rowid}: '{amount}' -> {float_amount}")
                    
            except (ValueError, TypeError):
                # If we can't convert, delete the invalid record
                cursor.execute("DELETE FROM Withdraw WHERE rowid = ?", (rowid,))
                deleted_count += 1
                print(f"Deleted invalid record {rowid}: Date={date}, Amount='{amount}', Description='{description}'")
        
        conn.commit()
        conn.close()
        
        print(f"Cleanup complete:")
        print(f"  Fixed {fixed_count} records")
        print(f"  Deleted {deleted_count} invalid records")
        return True
        
    except Exception as e:
        print(f"Error cleaning database: {e}")
        return False

if __name__ == "__main__":
    # Default database path
    db_path = "ozark_finances.db"
    
    if os.path.exists(db_path):
        clean_withdraw_amounts(db_path)
    else:
        print(f"Database file not found: {db_path}")
        print("Please run this script from the FlaskPort directory or specify the correct database path")
