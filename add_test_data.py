#!/usr/bin/env python3
"""
Add test invoice data to demonstrate sorting functionality
"""

import sqlite3
from datetime import datetime, timedelta
import random

def add_test_invoices():
    """Add sample invoices for testing sorting"""
    
    # Connect to database
    conn = sqlite3.connect('ozark_finances.db')
    cursor = conn.cursor()
    
    # Check if we already have data
    cursor.execute('SELECT COUNT(*) FROM Invoices')
    count = cursor.fetchone()[0]
    
    if count == 0:
        print('Adding sample invoice data...')
        
        # Add some sample invoices for testing sorting
        base_date = datetime(2025, 1, 1)
        
        for i in range(20):
            invoice_id = 25000 + i + 1
            date_offset = random.randint(0, 200)
            invoice_date = (base_date + timedelta(days=date_offset)).strftime('%d-%m-%Y')
            amount_excl = round(random.uniform(100, 2000), 2)
            btw = round(amount_excl * 0.21, 2)
            incl = round(amount_excl + btw, 2)
            
            cursor.execute(
                'INSERT INTO Invoices (InvoiceID, InvoiceDate, Excl, BTW, Incl) VALUES (?, ?, ?, ?, ?)',
                (str(invoice_id), invoice_date, amount_excl, btw, incl)
            )
        
        conn.commit()
        print(f'Added 20 sample invoices')
        
        # Show a few examples
        cursor.execute('SELECT InvoiceID, InvoiceDate, Excl, Incl FROM Invoices ORDER BY InvoiceID LIMIT 5')
        print('\nSample invoices added:')
        for row in cursor.fetchall():
            print(f"  Invoice {row[0]}: {row[1]} - €{row[2]:.2f} (Excl) / €{row[3]:.2f} (Incl)")
            
    else:
        print(f'Database already has {count} invoices')
        
        # Show current data
        cursor.execute('SELECT InvoiceID, InvoiceDate, Excl, Incl FROM Invoices ORDER BY CAST(InvoiceID AS INTEGER) DESC LIMIT 5')
        print('\nCurrent invoices (newest first):')
        for row in cursor.fetchall():
            print(f"  Invoice {row[0]}: {row[1]} - €{row[2]:.2f} (Excl) / €{row[3]:.2f} (Incl)")
    
    conn.close()

if __name__ == '__main__':
    add_test_invoices()
