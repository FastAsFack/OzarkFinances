#!/usr/bin/env python3
"""
Debug script to test multi-file import functionality
"""

import os
import sys
import logging
import tempfile
from datetime import datetime

# Add the current directory to the path so we can import from app.py
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the necessary functions from app.py
try:
    from app import process_excel_import, db_manager
    print("✅ Successfully imported functions from app.py")
except ImportError as e:
    print(f"❌ Failed to import from app.py: {e}")
    sys.exit(1)

def test_file_processing():
    """Test if we can identify what type of files the user is trying to import"""
    
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    print("🔍 Testing multi-file import debugging...")
    print(f"📅 Current time: {datetime.now()}")
    print()
    
    # Check if there are any sample Excel files in the workspace
    excel_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith(('.xlsx', '.xls')):
                excel_files.append(os.path.join(root, file))
    
    if excel_files:
        print(f"📋 Found {len(excel_files)} Excel files in workspace:")
        for i, file in enumerate(excel_files[:5], 1):  # Show first 5
            print(f"   {i}. {file}")
        if len(excel_files) > 5:
            print(f"   ... and {len(excel_files) - 5} more")
        print()
    else:
        print("❌ No Excel files found in workspace")
        print()
    
    # Check database connection
    try:
        # Test database connection
        test_result = db_manager.execute_query("SELECT COUNT(*) as count FROM Invoices LIMIT 1")
        print(f"✅ Database connection successful. Current invoice count: {test_result[0]['count']}")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        
    print()
    
    # Check if the process_excel_import function has the problematic return
    import inspect
    source = inspect.getsource(process_excel_import)
    if 'return imported_count' in source:
        # Count how many times it appears
        return_count = source.count('return imported_count')
        print(f"⚠️  Found {return_count} instances of 'return imported_count' in process_excel_import function")
        
        # Find the line numbers
        lines = source.split('\n')
        for i, line in enumerate(lines, 1):
            if 'return imported_count' in line:
                print(f"   Line {i}: {line.strip()}")
    
    print("\n" + "="*50)
    print("🎯 ANALYSIS:")
    print("The issue is likely that when you select multiple files,")
    print("JavaScript sends concurrent requests, but each request")
    print("might be interfering with each other, or files aren't")
    print("being uploaded properly in the concurrent scenario.")
    print("="*50)

if __name__ == "__main__":
    test_file_processing()
