#!/usr/bin/env python3
"""
Audit Logs Reset Script for Ozark Finances
Clears all audit logs from the audit_tracker.db database
"""

import os
import sqlite3
import sys
from datetime import datetime

def reset_audit_logs(audit_db_path="audit_tracker.db", confirm=True):
    """
    Reset all audit logs by clearing the audit database
    
    Args:
        audit_db_path (str): Path to the audit database file
        confirm (bool): Whether to ask for confirmation before clearing
    """
    
    # Get full path
    if not os.path.isabs(audit_db_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audit_db_path = os.path.join(script_dir, audit_db_path)
    
    print("🔄 AUDIT LOGS RESET UTILITY")
    print("=" * 50)
    print(f"📍 Database: {audit_db_path}")
    
    # Check if database exists
    if not os.path.exists(audit_db_path):
        print("❌ Audit database not found!")
        print(f"   Expected location: {audit_db_path}")
        return False
    
    # Get current log count
    try:
        with sqlite3.connect(audit_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            current_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM audit_log")
            date_range = cursor.fetchone()
            
        print(f"📊 Current audit logs: {current_count:,}")
        if date_range[0] and date_range[1]:
            print(f"📅 Date range: {date_range[0]} to {date_range[1]}")
        
    except sqlite3.Error as e:
        print(f"❌ Error reading database: {e}")
        return False
    
    if current_count == 0:
        print("✅ No audit logs to clear - database is already empty")
        return True
    
    # Confirmation prompt
    if confirm:
        print("\n⚠️  WARNING: This will permanently delete ALL audit logs!")
        print("   This action cannot be undone.")
        
        while True:
            response = input("\n🤔 Are you sure you want to clear all audit logs? (yes/no): ").lower().strip()
            if response in ['yes', 'y']:
                break
            elif response in ['no', 'n']:
                print("❌ Operation cancelled by user")
                return False
            else:
                print("Please enter 'yes' or 'no'")
    
    # Perform the reset
    try:
        print(f"\n🔄 Clearing {current_count:,} audit log entries...")
        
        with sqlite3.connect(audit_db_path) as conn:
            cursor = conn.cursor()
            
            # Clear all audit logs
            cursor.execute("DELETE FROM audit_log")
            
            # Reset auto-increment counter
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='audit_log'")
            
            # Vacuum to reclaim space
            cursor.execute("VACUUM")
            
            conn.commit()
            
        print("✅ Audit logs cleared successfully!")
        print("📊 Database reset and optimized")
        
        # Verify the clear
        with sqlite3.connect(audit_db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            remaining_count = cursor.fetchone()[0]
            
        if remaining_count == 0:
            print(f"✅ Verification: Database is now empty ({remaining_count} records)")
        else:
            print(f"⚠️  Warning: {remaining_count} records still remain")
            
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Error clearing audit logs: {e}")
        return False

def backup_audit_logs(audit_db_path="audit_tracker.db"):
    """
    Create a backup of the current audit logs before clearing
    
    Args:
        audit_db_path (str): Path to the audit database file
    """
    
    if not os.path.isabs(audit_db_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audit_db_path = os.path.join(script_dir, audit_db_path)
    
    if not os.path.exists(audit_db_path):
        print("❌ Cannot backup - audit database not found!")
        return None
    
    # Create backup filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = audit_db_path.replace('.db', f'_backup_{timestamp}.db')
    
    try:
        import shutil
        shutil.copy2(audit_db_path, backup_path)
        print(f"💾 Backup created: {os.path.basename(backup_path)}")
        return backup_path
    except Exception as e:
        print(f"❌ Backup failed: {e}")
        return None

def show_audit_statistics(audit_db_path="audit_tracker.db"):
    """
    Show current audit log statistics
    
    Args:
        audit_db_path (str): Path to the audit database file
    """
    
    if not os.path.isabs(audit_db_path):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        audit_db_path = os.path.join(script_dir, audit_db_path)
    
    if not os.path.exists(audit_db_path):
        print("❌ Audit database not found!")
        return
    
    try:
        with sqlite3.connect(audit_db_path) as conn:
            cursor = conn.cursor()
            
            # Total count
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            total_count = cursor.fetchone()[0]
            
            # Action breakdown
            cursor.execute("""
                SELECT action, COUNT(*) as count 
                FROM audit_log 
                GROUP BY action 
                ORDER BY count DESC
            """)
            actions = cursor.fetchall()
            
            # Table breakdown
            cursor.execute("""
                SELECT table_name, COUNT(*) as count 
                FROM audit_log 
                GROUP BY table_name 
                ORDER BY count DESC
            """)
            tables = cursor.fetchall()
            
            # Date range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM audit_log")
            date_range = cursor.fetchone()
            
            print("📊 AUDIT LOG STATISTICS")
            print("=" * 30)
            print(f"Total Records: {total_count:,}")
            
            if date_range[0] and date_range[1]:
                print(f"Date Range: {date_range[0]} to {date_range[1]}")
            
            if actions:
                print("\n📝 Actions Breakdown:")
                for action, count in actions:
                    print(f"   {action}: {count:,}")
            
            if tables:
                print("\n📋 Tables Breakdown:")
                for table, count in tables:
                    print(f"   {table}: {count:,}")
            
            # Database file size
            file_size = os.path.getsize(audit_db_path)
            size_mb = file_size / (1024 * 1024)
            print(f"\n💾 Database Size: {size_mb:.2f} MB")
            
    except sqlite3.Error as e:
        print(f"❌ Error reading statistics: {e}")

def main():
    """Main function for command line usage"""
    
    print("🛠️  OZARK FINANCES - AUDIT LOGS RESET UTILITY")
    print("=" * 55)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Reset Ozark Finances audit logs")
    parser.add_argument('--db', default='audit_tracker.db', help='Path to audit database file')
    parser.add_argument('--stats', action='store_true', help='Show statistics only (no reset)')
    parser.add_argument('--backup', action='store_true', help='Create backup before reset')
    parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    
    args = parser.parse_args()
    
    # Show statistics
    if args.stats:
        show_audit_statistics(args.db)
        return
    
    # Create backup if requested
    if args.backup:
        print("💾 Creating backup before reset...")
        backup_path = backup_audit_logs(args.db)
        if not backup_path:
            print("❌ Backup failed - aborting reset")
            return
        print()
    
    # Perform reset
    success = reset_audit_logs(args.db, confirm=not args.force)
    
    if success:
        print("\n🎉 Audit logs reset completed successfully!")
        print("\n📋 What was cleared:")
        print("   • All audit log entries")
        print("   • Auto-increment counters")
        print("   • Database optimized (VACUUM)")
        
        print("\n🔄 Next steps:")
        print("   • Restart audit viewer if running")
        print("   • New audit logs will start from ID 1")
        print("   • Main application will continue tracking")
        
    else:
        print("\n❌ Audit logs reset failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
