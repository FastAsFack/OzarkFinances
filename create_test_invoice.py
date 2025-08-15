"""
Create a test Excel file for import testing
"""

import openpyxl
from datetime import datetime
import os

def create_test_invoice_excel():
    """Create a test Excel file with invoice data"""
    
    # Create a new workbook
    workbook = openpyxl.Workbook()
    worksheet = workbook.active
    worksheet.title = "Invoice"
    
    # Add some basic invoice data in Template.xlsx format
    worksheet['C13'] = '250101'  # Invoice number
    worksheet['C14'] = '23-07-2025'  # Invoice date
    worksheet['F18'] = 100.00  # Amount excluding BTW
    
    # Add some headers to make it look like an invoice
    worksheet['A1'] = "INVOICE"
    worksheet['A1'].font = openpyxl.styles.Font(size=20, bold=True)
    
    worksheet['A13'] = "Invoice Number:"
    worksheet['A14'] = "Invoice Date:"
    worksheet['A18'] = "Amount (Excl BTW):"
    
    # Save the test file
    output_path = "test_invoice.xlsx"
    workbook.save(output_path)
    print(f"✅ Test invoice created: {output_path}")
    
    return output_path

if __name__ == "__main__":
    create_test_invoice_excel()
