#!/usr/bin/env python3
"""
Database migration: Add Description column to Withdraw table
"""

import sqlite3
import os

def migrate_database(db_path):
    """Add Description column to Withdraw table if it doesn't exist"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if Description column exists
        cursor.execute("PRAGMA table_info(Withdraw)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'Description' not in columns:
            print("Adding Description column to Withdraw table...")
            cursor.execute("ALTER TABLE Withdraw ADD COLUMN Description TEXT DEFAULT ''")
            print("✓ Description column added successfully")
        else:
            print("✓ Description column already exists")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"Error migrating database: {e}")
        return False

if __name__ == "__main__":
    # Default database path
    db_path = "ozark_finances.db"
    
    if os.path.exists(db_path):
        migrate_database(db_path)
    else:
        print(f"Database file not found: {db_path}")
        print("Please run this script from the FlaskPort directory or specify the correct database path")
