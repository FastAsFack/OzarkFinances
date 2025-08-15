#!/usr/bin/env python3
"""
Database migration script to add new columns to DebtRegister table
for enhanced debt management features.
"""

import sqlite3
import os
from pathlib import Path

def migrate_debt_schema():
    """Add new columns to DebtRegister table if they don't exist"""
    
    # Get database path
    db_path = Path(__file__).parent / 'ozark_finances.db'
    
    if not db_path.exists():
        print(f"Database not found at: {db_path}")
        return False
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Get current table schema
            cursor.execute("PRAGMA table_info(DebtRegister)")
            columns = cursor.fetchall()
            existing_columns = [col[1] for col in columns]
            
            print(f"Existing columns: {existing_columns}")
            
            # Define new columns to add
            new_columns = [
                ('Category', 'TEXT'),
                ('DueDate', 'TEXT'),
                ('MinimumPayment', 'REAL'),
                ('InterestRate', 'REAL'),
                ('Notes', 'TEXT'),
                ('AddedDate', 'TEXT')
            ]
            
            # Add missing columns
            added_columns = []
            for column_name, column_type in new_columns:
                if column_name not in existing_columns:
                    try:
                        cursor.execute(f"ALTER TABLE DebtRegister ADD COLUMN {column_name} {column_type}")
                        added_columns.append(column_name)
                        print(f"Added column: {column_name} ({column_type})")
                    except sqlite3.Error as e:
                        print(f"Error adding column {column_name}: {e}")
            
            # Set AddedDate for existing records that don't have it
            if 'AddedDate' in added_columns:
                from datetime import datetime
                current_date = datetime.now().strftime('%Y-%m-%d')
                cursor.execute(
                    "UPDATE DebtRegister SET AddedDate = ? WHERE AddedDate IS NULL",
                    (current_date,)
                )
                updated_rows = cursor.rowcount
                print(f"Set AddedDate for {updated_rows} existing records")
            
            conn.commit()
            
            if added_columns:
                print(f"Successfully added {len(added_columns)} new columns: {', '.join(added_columns)}")
            else:
                print("All columns already exist - no migration needed")
            
            # Verify the new schema
            cursor.execute("PRAGMA table_info(DebtRegister)")
            final_columns = cursor.fetchall()
            print(f"Final schema: {[col[1] for col in final_columns]}")
            
            return True
            
    except Exception as e:
        print(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("Starting debt schema migration...")
    success = migrate_debt_schema()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")
