#!/usr/bin/env python3
"""
Docker initialization script for Ozark Finances
Ensures database and directories are properly set up in Docker environment
"""

import os
import sys
import sqlite3
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ensure_directories():
    """Ensure all required directories exist"""
    directories = [
        '/app/data',
        '/app/uploads', 
        '/app/generated',
        '/app/logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        logger.info(f"✓ Directory ensured: {directory}")
        
        # Set proper permissions (readable/writable by app)
        try:
            os.chmod(directory, 0o755)
        except Exception as e:
            logger.warning(f"Could not set permissions on {directory}: {e}")

def init_database():
    """Initialize the SQLite database with all required tables"""
    db_path = os.environ.get('DATABASE_PATH', '/app/data/ozark_finances.db')
    
    # Ensure the directory exists
    db_dir = os.path.dirname(db_path)
    Path(db_dir).mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Initializing database at: {db_path}")
    
    try:
        # Test if we can create/access the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Create Invoices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Invoices (
                InvoiceID TEXT PRIMARY KEY,
                InvoiceDate TEXT NOT NULL,
                Excl REAL NOT NULL,
                BTW REAL NOT NULL,
                Incl REAL NOT NULL,
                status TEXT DEFAULT 'active',
                deleted_at TEXT NULL,
                payment_status TEXT DEFAULT 'pending'
            )
        """)
        
        # Create Withdraw table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Withdraw (
                Date TEXT NOT NULL,
                Amount REAL NOT NULL
            )
        """)
        
        # Create KwartaalData table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS KwartaalData (
                tijdvak TEXT NOT NULL,
                betaling TEXT NOT NULL,
                kenmerk TEXT PRIMARY KEY,
                betaald TEXT NOT NULL,
                Amount REAL NOT NULL
            )
        """)
        
        # Create DebtRegister table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS DebtRegister (
                DebtName TEXT PRIMARY KEY,
                Amount REAL NOT NULL,
                UnixStamp INTEGER NOT NULL,
                OriginalDebt REAL NOT NULL
            )
        """)
        
        # Commit and close
        conn.commit()
        conn.close()
        
        logger.info("✅ Database initialization completed successfully")
        
        # Verify database file exists and is accessible
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            logger.info(f"✅ Database file created: {db_path} ({file_size} bytes)")
            
            # Test read access
            test_conn = sqlite3.connect(db_path)
            test_cursor = test_conn.cursor()
            test_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = test_cursor.fetchall()
            test_conn.close()
            logger.info(f"✅ Database tables verified: {[table[0] for table in tables]}")
            
            # Test a simple query on each table
            test_conn = sqlite3.connect(db_path)
            test_cursor = test_conn.cursor()
            for table in ['Invoices', 'Withdraw', 'KwartaalData', 'DebtRegister']:
                try:
                    test_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = test_cursor.fetchone()[0]
                    logger.info(f"✅ Table {table}: {count} records")
                except Exception as e:
                    logger.error(f"❌ Error testing table {table}: {e}")
            test_conn.close()
            
        else:
            logger.error(f"❌ Database file was not created at {db_path}")
            logger.error(f"Directory contents: {os.listdir(db_dir) if os.path.exists(db_dir) else 'Directory does not exist'}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        logger.error(f"Working directory: {os.getcwd()}")
        logger.error(f"Database path: {db_path}")
        logger.error(f"Database directory exists: {os.path.exists(db_dir)}")
        logger.error(f"Database directory writable: {os.access(db_dir, os.W_OK)}")
        return False
    
    return True

def verify_environment():
    """Verify Docker environment is properly configured"""
    logger.info("🔍 Verifying Docker environment...")
    
    # Check environment variables
    env_vars = ['DATABASE_PATH', 'DATA_DIR', 'UPLOAD_FOLDER', 'GENERATED_FOLDER']
    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        logger.info(f"  {var}: {value}")
    
    # Check current working directory
    logger.info(f"  Working directory: {os.getcwd()}")
    
    # Check if we're running as expected user
    try:
        logger.info(f"  User ID: {os.getuid()}")
        logger.info(f"  Group ID: {os.getgid()}")
    except AttributeError:
        logger.info("  User ID: Unknown (Windows)")
    
    # Check mounted volumes
    paths_to_check = ['/app/data', '/app/uploads', '/app/generated', '/app/logs']
    for path in paths_to_check:
        exists = os.path.exists(path)
        writable = os.access(path, os.W_OK) if exists else False
        readable = os.access(path, os.R_OK) if exists else False
        logger.info(f"  {path}: exists={exists}, readable={readable}, writable={writable}")
        
        if exists:
            try:
                # List contents
                contents = os.listdir(path)
                logger.info(f"    Contents: {contents[:5]}{'...' if len(contents) > 5 else ''}")
            except PermissionError as e:
                logger.warning(f"    Cannot list contents: {e}")

def main():
    """Main initialization function"""
    logger.info("🚀 Starting Docker initialization for Ozark Finances...")
    
    try:
        # Verify environment
        verify_environment()
        
        # Ensure directories exist
        ensure_directories()
        
        # Initialize database
        if not init_database():
            logger.error("❌ Database initialization failed!")
            sys.exit(1)
        
        logger.info("🎉 Docker initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Initialization failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
