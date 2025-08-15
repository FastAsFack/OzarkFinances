#!/usr/bin/env python3
"""
Test script to verify the validation fix for edit invoice form.
This script will simulate the validation that happens when saving changes.
"""

import sys
import os

# Add the FlaskPort directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, DatabaseManager

def test_invoice_validation():
    """Test the invoice validation logic"""
    
    print("🧪 Testing Invoice Validation Fix")
    print("=" * 50)
    
    # Test data - simulating form submission
    test_cases = [
        {
            "name": "Valid invoice data",
            "data": {
                "invoice_date": "2025-07-26",
                "amount_excl": "100.00",
                "amount_btw": "21.00", 
                "amount_incl": "121.00",
                "payment_status": "pending"
            },
            "should_pass": True
        },
        {
            "name": "Missing required date",
            "data": {
                "invoice_date": "",
                "amount_excl": "100.00",
                "amount_btw": "21.00",
                "amount_incl": "121.00", 
                "payment_status": "pending"
            },
            "should_pass": False
        },
        {
            "name": "Invalid amount format",
            "data": {
                "invoice_date": "2025-07-26",
                "amount_excl": "abc",
                "amount_btw": "21.00",
                "amount_incl": "121.00",
                "payment_status": "pending"
            },
            "should_pass": False
        },
        {
            "name": "Empty required fields",
            "data": {
                "invoice_date": "",
                "amount_excl": "",
                "amount_btw": "",
                "amount_incl": "",
                "payment_status": "pending"
            },
            "should_pass": False
        }
    ]
    
    with app.app_context():
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📋 Test Case {i}: {test_case['name']}")
            print("-" * 30)
            
            # Simulate the validation logic from app.py
            errors = validate_invoice_data(test_case['data'])
            
            print(f"📊 Input data: {test_case['data']}")
            print(f"⚠️  Validation errors: {errors}")
            print(f"✅ Expected to pass: {test_case['should_pass']}")
            print(f"🎯 Actually passed: {len(errors) == 0}")
            
            # Check if test passed expectations
            passed_validation = len(errors) == 0
            if passed_validation == test_case['should_pass']:
                print("✅ Test PASSED")
            else:
                print("❌ Test FAILED")
                
            # Check for "true" errors
            if any(str(error).lower() == 'true' for error in errors):
                print("🚨 WARNING: Found 'true' error values!")
                print(f"🔍 Error types: {[type(error) for error in errors]}")

def validate_invoice_data(data):
    """Replicate the validation logic from app.py"""
    from datetime import datetime
    
    errors = []
    
    invoice_date = data.get('invoice_date', '').strip()
    amount_excl_str = data.get('amount_excl', '').strip()
    amount_btw_str = data.get('amount_btw', '').strip()
    amount_incl_str = data.get('amount_incl', '').strip()
    payment_status = data.get('payment_status', 'pending')
    
    # Validate date
    if not invoice_date:
        errors.append("Invoice date is required")
    else:
        try:
            # Check if date format is correct (YYYY-MM-DD)
            datetime.strptime(invoice_date, '%Y-%m-%d')
        except ValueError:
            errors.append("Invalid date format")
    
    # Parse amounts with European format support
    def parse_amount(amount_str, field_name):
        if not amount_str:
            errors.append(f"{field_name} is required")
            return None
        
        # Handle European decimal format (comma as decimal separator)
        cleaned_amount = amount_str.replace(',', '.')
        try:
            amount = float(cleaned_amount)
            if amount < 0:
                errors.append(f"{field_name} cannot be negative")
                return None
            return round(amount, 2)
        except ValueError:
            errors.append(f"Invalid {field_name.lower()} format")
            return None
    
    amount_excl = parse_amount(amount_excl_str, "Amount excluding BTW")
    amount_btw = parse_amount(amount_btw_str, "BTW amount")
    amount_incl = parse_amount(amount_incl_str, "Amount including BTW")
    
    # Validate BTW calculation (allow for small rounding differences)
    if amount_excl is not None and amount_btw is not None and amount_incl is not None:
        calculated_btw = round(amount_excl * 0.21, 2)
        calculated_incl = round(amount_excl + amount_btw, 2)
        
        # Allow for small rounding differences (±0.01)
        if abs(amount_btw - calculated_btw) > 0.01:
            errors.append(f"BTW amount should be approximately €{calculated_btw:.2f} (21% of €{amount_excl:.2f})")
        
        if abs(amount_incl - calculated_incl) > 0.01:
            errors.append(f"Total amount should be €{calculated_incl:.2f} (excl + BTW)")
    
    # Validate payment status
    valid_statuses = ['pending', 'paid', 'overdue', 'draft']
    if payment_status not in valid_statuses:
        errors.append("Invalid payment status")
    
    return errors

if __name__ == "__main__":
    test_invoice_validation()
    print("\n🎯 Validation test completed!")
