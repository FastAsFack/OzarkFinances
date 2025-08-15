#!/usr/bin/env python3
"""
Migrate individual debt database files to add missing columns
"""

import sqlite3
import os
from pathlib import Path

def migrate_debt_databases():
    """Add missing columns to existing debt database files"""
    
    # Get all .sqlite files (individual debt databases)
    debt_files = list(Path('.').glob('*.sqlite'))
    debt_files = [f for f in debt_files if f.name != 'ozark_finances.db' and f.name != 'audit_tracker.db']
    
    print(f"Found {len(debt_files)} debt database files to migrate")
    
    for debt_file in debt_files:
        print(f"\nMigrating {debt_file}...")
        
        try:
            with sqlite3.connect(debt_file) as conn:
                cursor = conn.cursor()
                
                # Check current table structure
                cursor.execute("PRAGMA table_info(DebtSource)")
                columns = {col[1]: col[2] for col in cursor.fetchall()}
                print(f"  Current columns: {list(columns.keys())}")
                
                # Add missing columns if they don't exist
                migrations_applied = []
                
                if 'PaymentMethod' not in columns:
                    cursor.execute("ALTER TABLE DebtSource ADD COLUMN PaymentMethod TEXT")
                    migrations_applied.append("PaymentMethod")
                
                if 'Notes' not in columns:
                    cursor.execute("ALTER TABLE DebtSource ADD COLUMN Notes TEXT")
                    migrations_applied.append("Notes")
                
                if migrations_applied:
                    print(f"  ✓ Added columns: {', '.join(migrations_applied)}")
                    conn.commit()
                else:
                    print(f"  ✓ Already up to date")
                    
        except Exception as e:
            print(f"  ✗ Error migrating {debt_file}: {e}")
    
    print("\nMigration completed!")

if __name__ == "__main__":
    migrate_debt_databases()
