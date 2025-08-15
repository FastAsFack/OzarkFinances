"""
Debug script for Ozark Finances Flask Application
This script helps identify and fix common issues
"""

import sqlite3
import os
from pathlib import Path

def check_database():
    """Check if database exists and has correct structure"""
    db_path = '../data/FinanceData.sqlite'
    
    print("Database Check")
    print("=" * 30)
    
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        print("Run init_db.py to create the database")
        return False
    
    print(f"✅ Database found at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check tables
        tables = ['Invoices', 'Withdraw', 'KwartaalData', 'DebtRegister']
        
        for table in tables:
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
            if cursor.fetchone():
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"✅ Table {table}: {count} records")
            else:
                print(f"❌ Table {table}: NOT FOUND")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_routes():
    """Test Flask application routes"""
    print("\nRoute Testing")
    print("=" * 30)
    
    try:
        from app import app
        
        with app.test_client() as client:
            routes = [
                ('/', 'Dashboard'),
                ('/invoices', 'Invoices'),
                ('/withdraws', 'Withdraws'),
                ('/important-info', 'Important Info'),
                ('/debt', 'Debt Management'),
                ('/card-variations', 'Card Design Variations')
            ]
            
            for route, name in routes:
                try:
                    response = client.get(route)
                    if response.status_code == 200:
                        print(f"✅ {name} ({route}): OK")
                    else:
                        print(f"❌ {name} ({route}): Status {response.status_code}")
                except Exception as e:
                    print(f"❌ {name} ({route}): Error - {e}")
        
    except Exception as e:
        print(f"❌ Flask app error: {e}")

def check_templates():
    """Check if all template files exist"""
    print("\nTemplate Check")
    print("=" * 30)
    
    templates = [
        'base.html',
        'index.html', 
        'invoices.html',
        'withdraws.html',
        'important_info.html',
        'debt.html',
        'debt_log.html',
        'card_variations.html'
    ]
    
    template_dir = Path('templates')
    
    for template in templates:
        template_path = template_dir / template
        if template_path.exists():
            print(f"✅ {template}: Found")
        else:
            print(f"❌ {template}: NOT FOUND")

def check_requirements():
    """Check if required packages are installed"""
    print("\nRequirements Check")
    print("=" * 30)
    
    requirements = ['flask', 'openpyxl']
    
    for req in requirements:
        try:
            __import__(req)
            print(f"✅ {req}: Installed")
        except ImportError:
            print(f"❌ {req}: NOT INSTALLED")

def main():
    """Run all checks"""
    print("Ozark Finances Flask Debug Tool")
    print("=" * 40)
    
    check_requirements()
    check_database()
    check_templates()
    test_routes()
    
    print("\nDebug complete!")
    print("If you see any ❌ errors above, fix them before running the app.")

if __name__ == "__main__":
    main()
    input("\nPress Enter to exit...")
