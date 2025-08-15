#!/usr/bin/env python3
"""
Direct test of process_excel_import function with multiple files
"""

import os
import sys
import sqlite3
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

def test_direct_excel_processing():
    """Test the process_excel_import function directly with multiple files"""
    
    print("🧪 Testing Direct Excel Processing")
    print("=" * 50)
    
    # Test files from the workspace
    test_files = [
        "Template.xlsx",
        "test_invoice.xlsx", 
        "test_simple_invoice.xlsx"
    ]
    
    # Check which files exist
    existing_files = []
    for file in test_files:
        if os.path.exists(file):
            existing_files.append(file)
            print(f"✅ Found: {file}")
        else:
            print(f"❌ Missing: {file}")
    
    if not existing_files:
        print("❌ No test files found! Cannot proceed.")
        return
    
    print(f"\n🎯 Testing with {len(existing_files)} files")
    
    # Get initial invoice count
    try:
        initial_count_result = db_manager.execute_query("SELECT COUNT(*) as count FROM Invoices")
        initial_count = initial_count_result[0]['count'] if initial_count_result else 0
        print(f"📊 Initial invoice count: {initial_count}")
    except Exception as e:
        print(f"❌ Error getting initial count: {e}")
        return
    
    # Process each file individually and track results
    results = []
    total_imported = 0
    
    for i, file_path in enumerate(existing_files, 1):
        print(f"\n🔄 Processing file {i}/{len(existing_files)}: {file_path}")
        
        try:
            # Process the file
            imported_count = process_excel_import(file_path)
            
            result = {
                'file': file_path,
                'imported_count': imported_count,
                'success': imported_count > 0,
                'error': None
            }
            
            total_imported += imported_count
            results.append(result)
            
            if imported_count > 0:
                print(f"✅ Imported {imported_count} invoice(s) from {file_path}")
            else:
                print(f"⚠️  No invoices imported from {file_path}")
                
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
            results.append({
                'file': file_path,
                'imported_count': 0,
                'success': False,
                'error': str(e)
            })
    
    # Get final invoice count
    try:
        final_count_result = db_manager.execute_query("SELECT COUNT(*) as count FROM Invoices")
        final_count = final_count_result[0]['count'] if final_count_result else 0
        print(f"\n📊 Final invoice count: {final_count}")
        actual_increase = final_count - initial_count
        print(f"📈 Actual increase: {actual_increase}")
    except Exception as e:
        print(f"❌ Error getting final count: {e}")
        actual_increase = 0
    
    # Summary
    print(f"\n📊 RESULTS SUMMARY")
    print("=" * 50)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"📈 Total files processed: {len(results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📋 Expected total imports: {total_imported}")
    print(f"🎯 Actual database increase: {actual_increase}")
    
    # Detailed results
    print(f"\n📋 DETAILED RESULTS:")
    for result in results:
        status = "✅" if result['success'] else "❌"
        error_msg = f" (Error: {result['error']})" if result['error'] else ""
        print(f"   {status} {result['file']}: {result['imported_count']} imported{error_msg}")
    
    # Check for issues
    if total_imported != actual_increase:
        print(f"\n⚠️  DISCREPANCY DETECTED!")
        print(f"   Expected: {total_imported} imports")
        print(f"   Actual: {actual_increase} imports")
        print("   This could indicate duplicate detection or database issues.")
    
    if len(successful) == len(existing_files) and actual_increase > 0:
        print(f"\n🎉 SUCCESS: All files processed and invoices imported!")
    elif len(successful) < len(existing_files):
        print(f"\n⚠️  PARTIAL SUCCESS: Only {len(successful)} out of {len(existing_files)} files processed successfully.")
    
    # Show recent invoices
    try:
        recent_invoices = db_manager.execute_query("""
            SELECT InvoiceID, InvoiceDate, Excl 
            FROM Invoices 
            ORDER BY rowid DESC 
            LIMIT 10
        """)
        
        if recent_invoices:
            print(f"\n📋 Recent invoices in database:")
            for invoice in recent_invoices:
                print(f"   • Invoice {invoice['InvoiceID']}: {invoice['InvoiceDate']} - €{invoice['Excl']}")
    except Exception as e:
        print(f"❌ Error getting recent invoices: {e}")

if __name__ == "__main__":
    test_direct_excel_processing()
