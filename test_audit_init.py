"""
Quick test of audit database functions
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from init_audit_db import verify_audit_database, show_audit_statistics

if __name__ == "__main__":
    print("🧪 Testing audit database functions...")
    
    # Test verification
    print("\n1. Verifying existing database...")
    verify_result = verify_audit_database()
    
    # Test statistics
    print("\n2. Showing statistics...")
    show_audit_statistics()
    
    print("\n✅ Test completed!")
