#!/usr/bin/env python3
"""
Test script to generate sample audit data for Feature #3 demonstration
"""

from audit_tracker import audit_tracker, audit_transaction
from datetime import datetime
import json

def main():
    print("🔍 Testing Feature #3: Comprehensive Audit Trail")
    print("=" * 60)
    
    # Test 1: System startup
    print("1. Logging system startup...")
    audit_tracker.log_action(
        action="SYSTEM_START",
        table_name="SYSTEM",
        record_id="STARTUP",
        user_info={
            "action": "Application startup",
            "timestamp": datetime.now().isoformat(),
            "feature_test": "Feature #3 - Comprehensive Audit Trail"
        }
    )
    
    # Test 2: Transaction example
    print("2. Testing transaction logging...")
    with audit_transaction("Invoice Creation Test", {"user": "test_user", "feature": "audit_test"}):
        audit_tracker.log_action(
            action="INSERT",
            table_name="Invoices",
            record_id="TEST001",
            new_values={
                "InvoiceID": "TEST001",
                "InvoiceDate": "14-01-2025",
                "Excl": 100.00,
                "BTW": 21.00,
                "Incl": 121.00,
                "payment_status": "pending"
            },
            user_info={"operation": "create_test_invoice", "test": True}
        )
        
        # Simulate an update
        audit_tracker.log_action(
            action="UPDATE",
            table_name="Invoices",
            record_id="TEST001",
            old_values={
                "InvoiceID": "TEST001",
                "InvoiceDate": "14-01-2025",
                "Excl": 100.00,
                "BTW": 21.00,
                "Incl": 121.00,
                "payment_status": "pending"
            },
            new_values={
                "InvoiceID": "TEST001",
                "InvoiceDate": "14-01-2025",
                "Excl": 150.00,
                "BTW": 31.50,
                "Incl": 181.50,
                "payment_status": "paid"
            },
            user_info={"operation": "update_test_invoice", "test": True}
        )
    
    # Test 3: Multiple table operations
    print("3. Testing multiple table operations...")
    
    # Withdraw operation
    audit_tracker.log_action(
        action="INSERT",
        table_name="Withdraw",
        record_id="W001",
        new_values={
            "Date": "2025-01-14",
            "Amount": -25.50,
            "Description": "Test withdrawal for audit trail"
        },
        user_info={"operation": "test_withdraw", "test": True}
    )
    
    # Debt operation
    audit_tracker.log_action(
        action="INSERT",
        table_name="DebtRegister",
        record_id="TestDebt",
        new_values={
            "DebtName": "TestDebt",
            "Amount": 1000.00,
            "OriginalDebt": 1000.00,
            "UnixStamp": int(datetime.now().timestamp())
        },
        user_info={"operation": "test_debt", "test": True}
    )
    
    # Test 4: Error simulation
    print("4. Testing error logging...")
    audit_tracker.log_action(
        action="ERROR",
        table_name="SYSTEM",
        record_id="ERR001",
        user_info={
            "error_type": "test_error",
            "message": "Simulated error for audit trail testing",
            "severity": "low",
            "test": True
        }
    )
    
    # Test 5: Field-level changes
    print("5. Testing field-level change tracking...")
    audit_tracker.log_action(
        action="UPDATE",
        table_name="Invoices",
        record_id="TEST002",
        old_values={
            "InvoiceID": "TEST002",
            "InvoiceDate": "14-01-2025",
            "Excl": 200.00,
            "BTW": 42.00,
            "Incl": 242.00,
            "payment_status": "pending",
            "notes": "Original notes"
        },
        new_values={
            "InvoiceID": "TEST002",
            "InvoiceDate": "15-01-2025",  # Date changed
            "Excl": 250.00,              # Amount changed
            "BTW": 52.50,                # BTW recalculated
            "Incl": 302.50,              # Total recalculated
            "payment_status": "paid",     # Status changed
            "notes": "Updated notes"      # Notes changed
        },
        user_info={"operation": "comprehensive_update_test", "test": True}
    )
    
    # Get statistics
    print("\n📊 Audit Statistics:")
    stats = audit_tracker.get_statistics()
    
    print(f"Total actions logged: {stats['overall'].get('total_actions', 0)}")
    print(f"Tables tracked: {stats['overall'].get('tables_tracked', 0)}")
    print(f"Records affected: {stats['overall'].get('records_affected', 0)}")
    print(f"Recent activity (24h): {stats['recent_activity'].get('count', 0)}")
    
    print("\n📋 Action breakdown:")
    for action in stats['actions']:
        print(f"  {action['action']}: {action['count']} times")
    
    print("\n🗂️ Table activity:")
    for table in stats['tables']:
        print(f"  {table['table_name']}: {table['count']} actions")
    
    print("\n✅ Feature #3 test completed!")
    print("🌐 Access audit viewer at: http://localhost:5001")
    print("📁 Audit database: audit_tracker.db")
    print("🔍 Check logs with advanced filtering and search")

if __name__ == "__main__":
    main()
