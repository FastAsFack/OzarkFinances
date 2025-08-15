#!/usr/bin/env python3
"""
Test script to simulate multi-file import functionality
"""

import os
import sys
import requests
import tempfile
import shutil
from pathlib import Path

# Test files from the workspace
test_files = [
    "Template.xlsx",
    "test_invoice.xlsx", 
    "test_simple_invoice.xlsx"
]

def test_multifile_import():
    """Test importing multiple files like the JavaScript would do"""
    
    print("🧪 Testing Multi-File Import Simulation")
    print("=" * 50)
    
    # Check if Flask app is running (we'll assume it's running on localhost:5000)
    base_url = "http://localhost:5000"
    import_url = f"{base_url}/api/invoices/import"
    
    print(f"📡 Testing endpoint: {import_url}")
    
    # Check if files exist
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
    
    print(f"\n🎯 Will test with {len(existing_files)} files")
    
    # Test if server is running
    try:
        response = requests.get(base_url, timeout=5)
        print(f"✅ Server is running (status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ Server not accessible: {e}")
        print("💡 Please start the Flask app first with: python app.py")
        return
    
    # Simulate concurrent file uploads like JavaScript does
    import concurrent.futures
    import time
    
    def upload_file(file_path):
        """Upload a single file and return the result"""
        file_name = os.path.basename(file_path)
        start_time = time.time()
        
        try:
            with open(file_path, 'rb') as f:
                files = {'file': (file_name, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                response = requests.post(import_url, files=files, timeout=30)
                
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            
            result = {
                'file': file_name,
                'status_code': response.status_code,
                'duration': duration,
                'success': False,
                'message': 'Unknown error'
            }
            
            if response.status_code == 200:
                try:
                    json_data = response.json()
                    result['success'] = json_data.get('status') == 'success'
                    result['message'] = json_data.get('message', 'No message')
                    result['imported_count'] = json_data.get('imported_count', 0)
                except:
                    result['message'] = 'Failed to parse JSON response'
            else:
                result['message'] = f'HTTP {response.status_code}: {response.text[:100]}'
                
            return result
            
        except Exception as e:
            end_time = time.time()
            duration = round(end_time - start_time, 2)
            return {
                'file': file_name,
                'status_code': 0,
                'duration': duration,
                'success': False,
                'message': str(e),
                'imported_count': 0
            }
    
    print(f"\n🚀 Starting concurrent upload test...")
    
    # Test concurrent uploads (like JavaScript Promise.all)
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(existing_files)) as executor:
        future_to_file = {executor.submit(upload_file, file): file for file in existing_files}
        results = []
        
        for future in concurrent.futures.as_completed(future_to_file):
            file = future_to_file[future]
            try:
                result = future.result()
                results.append(result)
                
                status_emoji = "✅" if result['success'] else "❌"
                print(f"{status_emoji} {result['file']}: {result['message']} ({result['duration']}s)")
                
            except Exception as exc:
                print(f"❌ {file}: Exception occurred: {exc}")
                results.append({
                    'file': file,
                    'success': False,
                    'message': str(exc),
                    'imported_count': 0
                })
    
    # Summary
    print(f"\n📊 RESULTS SUMMARY")
    print("=" * 50)
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    total_imported = sum(r.get('imported_count', 0) for r in results)
    
    print(f"📈 Total files processed: {len(results)}")
    print(f"✅ Successful: {len(successful)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"📋 Total invoices imported: {total_imported}")
    
    if failed:
        print(f"\n❌ FAILED FILES:")
        for result in failed:
            print(f"   • {result['file']}: {result['message']}")
    
    if len(successful) == len(existing_files):
        print(f"\n🎉 SUCCESS: All files imported successfully!")
    elif len(successful) == 1 and len(existing_files) > 1:
        print(f"\n⚠️  ISSUE CONFIRMED: Only {len(successful)} out of {len(existing_files)} files imported!")
        print("   This matches the user's reported problem.")
    elif len(successful) > 1:
        print(f"\n✅ PARTIAL SUCCESS: {len(successful)} out of {len(existing_files)} files imported.")
    else:
        print(f"\n❌ COMPLETE FAILURE: No files were imported successfully.")

if __name__ == "__main__":
    test_multifile_import()
