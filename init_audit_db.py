"""
Audit Database Initialization Script for Ozark Finances
This script creates the audit tracking database and tables if they don't exist.
"""

import sqlite3
import os
from pathlib import Path
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database path
AUDIT_DATABASE_PATH = os.path.abspath('audit_tracker.db')

def init_audit_database(db_path=None):
    """Initialize the audit database with optimized structure"""
    
    if db_path is None:
        db_path = AUDIT_DATABASE_PATH
    
    print(f"🔄 Initializing audit database at: {db_path}")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Main audit log table
            print("📝 Creating audit_log table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    user_info TEXT,
                    changes TEXT,
                    old_values TEXT,
                    new_values TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    session_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            print("✅ audit_log table created/verified")
            
            # Performance indexes
            print("🚀 Creating performance indexes...")
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                ON audit_log(timestamp)
            """)
            print("✅ Timestamp index created")
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_table_action 
                ON audit_log(table_name, action)
            """)
            print("✅ Table/Action index created")
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_record_id 
                ON audit_log(record_id)
            """)
            print("✅ Record ID index created")
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_created_at 
                ON audit_log(created_at)
            """)
            print("✅ Created date index created")
            
            # Statistics view for dashboard
            print("📊 Creating audit statistics view...")
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS audit_statistics AS
                SELECT 
                    table_name,
                    action,
                    COUNT(*) as count,
                    MAX(timestamp) as last_activity,
                    MIN(timestamp) as first_activity,
                    DATE(created_at) as activity_date
                FROM audit_log
                GROUP BY table_name, action, DATE(created_at)
                ORDER BY last_activity DESC
            """)
            print("✅ Audit statistics view created")
            
            # Performance analytics view
            print("📈 Creating performance analytics view...")
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS audit_daily_summary AS
                SELECT 
                    DATE(created_at) as date,
                    table_name,
                    COUNT(*) as total_operations,
                    SUM(CASE WHEN action = 'INSERT' THEN 1 ELSE 0 END) as inserts,
                    SUM(CASE WHEN action = 'UPDATE' THEN 1 ELSE 0 END) as updates,
                    SUM(CASE WHEN action = 'DELETE' THEN 1 ELSE 0 END) as deletes,
                    SUM(CASE WHEN action = 'SELECT' THEN 1 ELSE 0 END) as selects
                FROM audit_log
                GROUP BY DATE(created_at), table_name
                ORDER BY date DESC, total_operations DESC
            """)
            print("✅ Daily summary view created")
            
            # User activity view
            print("👤 Creating user activity view...")
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS audit_user_activity AS
                SELECT 
                    user_info,
                    ip_address,
                    COUNT(*) as total_actions,
                    MAX(timestamp) as last_activity,
                    MIN(timestamp) as first_activity,
                    COUNT(DISTINCT table_name) as tables_accessed,
                    COUNT(DISTINCT DATE(created_at)) as active_days
                FROM audit_log
                WHERE user_info IS NOT NULL
                GROUP BY user_info, ip_address
                ORDER BY last_activity DESC
            """)
            print("✅ User activity view created")
            
            # Commit all changes
            conn.commit()
            
        print("\n🎉 Audit database initialization completed successfully!")
        logger.info(f"Audit database initialized at: {os.path.abspath(db_path)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error during audit database initialization: {e}")
        logger.error(f"Audit database initialization failed: {e}")
        return False

def verify_audit_database(db_path=None):
    """Verify the audit database structure"""
    
    if db_path is None:
        db_path = AUDIT_DATABASE_PATH
    
    if not os.path.exists(db_path):
        print(f"❌ Audit database not found at: {db_path}")
        return False
    
    print(f"\n🔍 Verifying audit database structure...")
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check main table
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'")
            if cursor.fetchone():
                print("✅ audit_log table exists")
            else:
                print("❌ audit_log table missing")
                return False
            
            # Check table structure
            cursor.execute("PRAGMA table_info(audit_log)")
            columns = cursor.fetchall()
            expected_columns = {
                'id', 'timestamp', 'action', 'table_name', 'record_id',
                'user_info', 'changes', 'old_values', 'new_values',
                'ip_address', 'user_agent', 'session_id', 'created_at'
            }
            actual_columns = {col[1] for col in columns}
            
            if expected_columns.issubset(actual_columns):
                print(f"✅ All required columns present ({len(actual_columns)} total)")
            else:
                missing = expected_columns - actual_columns
                print(f"❌ Missing columns: {missing}")
                return False
            
            # Check indexes
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='audit_log'")
            indexes = [row[0] for row in cursor.fetchall()]
            expected_indexes = ['idx_audit_timestamp', 'idx_audit_table_action', 'idx_audit_record_id']
            
            existing_indexes = [idx for idx in expected_indexes if idx in indexes]
            print(f"✅ Performance indexes: {len(existing_indexes)}/{len(expected_indexes)} present")
            
            # Check views
            cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
            views = [row[0] for row in cursor.fetchall()]
            expected_views = ['audit_statistics', 'audit_daily_summary', 'audit_user_activity']
            
            existing_views = [view for view in expected_views if view in views]
            print(f"✅ Analysis views: {len(existing_views)}/{len(expected_views)} present")
            
            # Check record count
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            record_count = cursor.fetchone()[0]
            print(f"📊 Current audit records: {record_count:,}")
            
            # Get database size
            db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
            print(f"💾 Database size: {db_size:.2f} MB")
            
        print("\n✅ Audit database verification completed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error during verification: {e}")
        logger.error(f"Audit database verification failed: {e}")
        return False

def show_audit_statistics(db_path=None):
    """Show current audit database statistics"""
    
    if db_path is None:
        db_path = AUDIT_DATABASE_PATH
    
    if not os.path.exists(db_path):
        print(f"❌ Audit database not found at: {db_path}")
        return
    
    print(f"\n📊 AUDIT DATABASE STATISTICS")
    print("=" * 50)
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Total records
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            total_records = cursor.fetchone()[0]
            print(f"📝 Total Records: {total_records:,}")
            
            if total_records == 0:
                print("📭 No audit records found - database is empty")
                return
            
            # Date range
            cursor.execute("SELECT MIN(timestamp), MAX(timestamp) FROM audit_log")
            date_range = cursor.fetchone()
            if date_range[0] and date_range[1]:
                print(f"📅 Date Range: {date_range[0]} to {date_range[1]}")
            
            # Actions breakdown
            print(f"\n📝 Actions Breakdown:")
            cursor.execute("""
                SELECT action, COUNT(*) as count 
                FROM audit_log 
                GROUP BY action 
                ORDER BY count DESC
            """)
            for action, count in cursor.fetchall():
                print(f"   {action}: {count:,}")
            
            # Tables breakdown
            print(f"\n📋 Tables Breakdown:")
            cursor.execute("""
                SELECT table_name, COUNT(*) as count 
                FROM audit_log 
                GROUP BY table_name 
                ORDER BY count DESC
            """)
            for table, count in cursor.fetchall():
                print(f"   {table}: {count:,}")
            
            # Recent activity (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) 
                FROM audit_log 
                WHERE datetime(created_at) > datetime('now', '-1 day')
            """)
            recent_count = cursor.fetchone()[0]
            print(f"\n🕐 Recent Activity (24h): {recent_count:,} records")
            
            # Database file size
            db_size = os.path.getsize(db_path) / (1024 * 1024)  # MB
            print(f"💾 Database Size: {db_size:.2f} MB")
            
    except Exception as e:
        print(f"\n❌ Error retrieving statistics: {e}")
        logger.error(f"Failed to retrieve audit statistics: {e}")

def recreate_audit_database(db_path=None):
    """Recreate the audit database (WARNING: This will delete all existing data!)"""
    
    if db_path is None:
        db_path = AUDIT_DATABASE_PATH
    
    print(f"\n⚠️  WARNING: This will completely recreate the audit database!")
    print(f"📍 Database path: {db_path}")
    
    if os.path.exists(db_path):
        print(f"🗃️  Existing database will be deleted!")
        
        # Show current stats before deletion
        show_audit_statistics(db_path)
        
        confirmation = input("\n❓ Are you sure you want to recreate the database? (yes/no): ").lower().strip()
        if confirmation not in ['yes', 'y']:
            print("❌ Operation cancelled")
            return False
        
        # Create backup
        backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"💾 Backup created: {backup_path}")
        except Exception as e:
            print(f"⚠️  Could not create backup: {e}")
            proceed = input("Continue without backup? (yes/no): ").lower().strip()
            if proceed not in ['yes', 'y']:
                print("❌ Operation cancelled")
                return False
        
        # Delete existing database
        try:
            os.remove(db_path)
            print(f"🗑️  Deleted existing database")
        except Exception as e:
            print(f"❌ Error deleting existing database: {e}")
            return False
    
    # Create new database
    print(f"\n🔄 Creating new audit database...")
    return init_audit_database(db_path)

def main():
    """Main function with interactive menu"""
    
    print("🛠️  AUDIT DATABASE INITIALIZATION UTILITY")
    print("=" * 50)
    print("Ozark Finances - Audit System Setup")
    print(f"Target database: {AUDIT_DATABASE_PATH}")
    
    while True:
        print(f"\n📋 Available Options:")
        print("1. Initialize audit database (safe - preserves existing data)")
        print("2. Verify audit database structure")
        print("3. Show audit database statistics")
        print("4. Recreate audit database (⚠️  WARNING: Deletes all data!)")
        print("5. Exit")
        
        choice = input("\n🔢 Enter your choice (1-5): ").strip()
        
        if choice == '1':
            print(f"\n🚀 Initializing audit database...")
            success = init_audit_database()
            if success:
                show_audit_statistics()
                
        elif choice == '2':
            verify_audit_database()
            
        elif choice == '3':
            show_audit_statistics()
            
        elif choice == '4':
            recreate_audit_database()
            
        elif choice == '5':
            print(f"\n👋 Goodbye!")
            break
            
        else:
            print(f"❌ Invalid choice. Please enter 1-5.")
    
    print(f"\n✅ Audit database utility completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n❌ Operation interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error in audit database utility: {e}")
    
    input("\nPress Enter to exit...")
