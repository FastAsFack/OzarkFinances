#!/usr/bin/env python3
"""
Create a test Excel file for testing the import functionality
"""

import openpyxl
from datetime import datetime
import os

def create_test_excel():
    """Create a test Excel file with invoice data"""
    
    # Create a new workbook
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Test Invoice"
    
    # Method 1: Create Template.xlsx format
    print("Creating Template.xlsx format test file...")
    
    # Add some header text
    worksheet['A1'] = "Test Invoice Data"
    worksheet['A1'].font = openpyxl.styles.Font(size=16, bold=True)
    
    # Add invoice data in Template.xlsx format
    worksheet['C13'] = 250001  # Invoice number
    worksheet['C14'] = datetime.now().strftime('%d-%m-%Y')  # Invoice date
    worksheet['F18'] = 150.00  # Amount excluding BTW
    
    # Also add data in alternative locations for testing
    worksheet['F43'] = 150.00  # Alternative amount location
    worksheet['F44'] = 31.50   # BTW amount (21% of 150)
    worksheet['F45'] = 181.50  # Total including BTW
    
    # Add some labels for clarity
    worksheet['B13'] = "Invoice Number:"
    worksheet['B14'] = "Invoice Date:"
    worksheet['E18'] = "Amount (Excl):"
    worksheet['E43'] = "Amount (Excl):"
    worksheet['E44'] = "BTW:"
    worksheet['E45'] = "Total (Incl):"
    
    # Save the file
    filename = "test_invoice.xlsx"
    workbook.save(filename)
    print(f"✅ Test Excel file created: {filename}")
    
    # Also create a simpler version with data in random cells
    workbook2 = openpyxl.Workbook()
    worksheet2 = workbook2.active
    worksheet2.title = "Simple Test"
    
    worksheet2['A1'] = "Simple Invoice Test"
    worksheet2['A3'] = "Invoice Number:"
    worksheet2['B3'] = 250002
    worksheet2['A4'] = "Amount:"
    worksheet2['B4'] = 75.50
    worksheet2['A5'] = "Date:"
    worksheet2['B5'] = datetime.now().strftime('%d-%m-%Y')
    
    filename2 = "test_simple_invoice.xlsx"
    workbook2.save(filename2)
    print(f"✅ Simple test Excel file created: {filename2}")
    
    print("\nTest files created successfully!")
    print("You can now test the import functionality with these files.")
    print(f"Files are located in: {os.getcwd()}")

if __name__ == "__main__":
    create_test_excel()
