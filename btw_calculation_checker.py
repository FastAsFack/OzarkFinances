#!/usr/bin/env python3
"""
BTW Calculation Checker
A diagnostic script to identify discrepancies in BTW (VAT) calculations
"""

import sqlite3
import os
from datetime import datetime, date
from decimal import Decimal, ROUND_HALF_UP

def connect_to_database():
    """Connect to the SQLite database"""
    # Try common database paths
    db_paths = [
        'ozark_finances.db',
        os.path.join(os.path.dirname(__file__), 'ozark_finances.db'),
        os.path.join(os.path.dirname(__file__), '..', 'ozark_finances.db')
    ]
    
    for db_path in db_paths:
        if os.path.exists(db_path):
            print(f"✅ Found database at: {db_path}")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            return conn
    
    print("❌ Database not found! Please specify the correct path.")
    print("Searched in:")
    for path in db_paths:
        print(f"  - {path}")
    return None

def check_invoice_statuses(conn):
    """Check all possible invoice statuses"""
    print("\n" + "="*60)
    print("📊 INVOICE STATUS ANALYSIS")
    print("="*60)
    
    cursor = conn.cursor()
    
    # Check all statuses
    cursor.execute("""
        SELECT 
            CASE 
                WHEN status IS NULL THEN 'NULL (no status)'
                ELSE status 
            END as status_display,
            status,
            COUNT(*) as count,
            SUM(BTW) as total_btw,
            SUM(Excl) as total_excl,
            SUM(Incl) as total_incl
        FROM Invoices 
        GROUP BY status
        ORDER BY count DESC
    """)
    
    results = cursor.fetchall()
    total_invoices = sum(row['count'] for row in results)
    
    print(f"Total invoices in database: {total_invoices}")
    print("\nBreakdown by status:")
    print("-" * 80)
    print(f"{'Status':<20} {'Count':<8} {'BTW Total':<12} {'Excl Total':<12} {'Incl Total':<12}")
    print("-" * 80)
    
    active_btw_total = 0
    for row in results:
        status = row['status_display']
        count = row['count']
        btw = row['total_btw'] or 0
        excl = row['total_excl'] or 0
        incl = row['total_incl'] or 0
        
        print(f"{status:<20} {count:<8} €{btw:<11.2f} €{excl:<11.2f} €{incl:<11.2f}")
        
        # Track active BTW (NULL or 'active' status)
        if row['status'] is None or row['status'] == 'active':
            active_btw_total += btw
    
    print("-" * 80)
    print(f"💰 Active BTW Total (NULL + 'active'): €{active_btw_total:.2f}")
    
    return active_btw_total

def check_date_ranges(conn):
    """Check BTW by year and current year focus"""
    print("\n" + "="*60)
    print("📅 DATE RANGE ANALYSIS")
    print("="*60)
    
    cursor = conn.cursor()
    current_year = str(date.today().year)
    
    # BTW by year
    cursor.execute("""
        SELECT 
            substr(InvoiceDate, 7, 4) as year,
            COUNT(*) as count,
            SUM(BTW) as total_btw,
            SUM(Excl) as total_excl
        FROM Invoices 
        WHERE (status IS NULL OR status = 'active')
        GROUP BY substr(InvoiceDate, 7, 4)
        ORDER BY year DESC
    """)
    
    years_data = cursor.fetchall()
    
    print("BTW by Year (Active invoices only):")
    print("-" * 50)
    print(f"{'Year':<8} {'Count':<8} {'BTW Total':<12} {'Excl Total':<12}")
    print("-" * 50)
    
    current_year_btw = 0
    for row in years_data:
        year = row['year']
        count = row['count']
        btw = row['total_btw'] or 0
        excl = row['total_excl'] or 0
        
        print(f"{year:<8} {count:<8} €{btw:<11.2f} €{excl:<11.2f}")
        
        if year == current_year:
            current_year_btw = btw
    
    print("-" * 50)
    print(f"💰 Current Year ({current_year}) BTW: €{current_year_btw:.2f}")
    
    return current_year_btw

def check_btw_calculation_accuracy(conn):
    """Check if stored BTW matches calculated BTW (21% of Excl)"""
    print("\n" + "="*60)
    print("🔍 BTW CALCULATION ACCURACY CHECK")
    print("="*60)
    
    cursor = conn.cursor()
    current_year = str(date.today().year)
    
    cursor.execute("""
        SELECT 
            InvoiceID,
            InvoiceDate,
            Excl,
            BTW as stored_btw,
            Incl,
            ROUND(Excl * 0.21, 2) as calculated_btw,
            ABS(BTW - ROUND(Excl * 0.21, 2)) as difference
        FROM Invoices 
        WHERE (status IS NULL OR status = 'active')
        AND substr(InvoiceDate, 7, 4) = ?
        ORDER BY difference DESC
    """, (current_year,))
    
    invoices = cursor.fetchall()
    
    total_stored_btw = 0
    total_calculated_btw = 0
    discrepancy_count = 0
    major_discrepancies = []
    
    print(f"Checking {len(invoices)} active invoices from {current_year}...")
    print("\nInvoices with BTW calculation issues (>€0.01 difference):")
    print("-" * 90)
    print(f"{'Invoice':<10} {'Date':<12} {'Excl':<10} {'Stored BTW':<12} {'Calc BTW':<12} {'Diff':<8}")
    print("-" * 90)
    
    for invoice in invoices:
        invoice_id = invoice['InvoiceID']
        date_str = invoice['InvoiceDate']
        excl = invoice['Excl'] or 0
        stored_btw = invoice['stored_btw'] or 0
        calculated_btw = invoice['calculated_btw'] or 0
        difference = invoice['difference'] or 0
        
        total_stored_btw += stored_btw
        total_calculated_btw += calculated_btw
        
        if difference > 0.01:  # More than 1 cent difference
            discrepancy_count += 1
            print(f"{invoice_id:<10} {date_str:<12} €{excl:<9.2f} €{stored_btw:<11.2f} €{calculated_btw:<11.2f} €{difference:<7.2f}")
            
            if difference > 1.00:  # Major discrepancy
                major_discrepancies.append({
                    'invoice_id': invoice_id,
                    'difference': difference,
                    'stored_btw': stored_btw,
                    'calculated_btw': calculated_btw
                })
    
    if discrepancy_count == 0:
        print("✅ No BTW calculation discrepancies found!")
    
    print("-" * 90)
    print(f"💰 Total Stored BTW:     €{total_stored_btw:.2f}")
    print(f"💰 Total Calculated BTW: €{total_calculated_btw:.2f}")
    print(f"💰 Overall Difference:   €{abs(total_stored_btw - total_calculated_btw):.2f}")
    print(f"⚠️  Invoices with issues: {discrepancy_count}")
    
    if major_discrepancies:
        print(f"\n🚨 MAJOR DISCREPANCIES (>€1.00):")
        for disc in major_discrepancies:
            print(f"   Invoice {disc['invoice_id']}: €{disc['difference']:.2f} difference")
    
    return total_stored_btw, total_calculated_btw

def check_quarterly_breakdown(conn):
    """Check quarterly BTW breakdown for current year"""
    print("\n" + "="*60)
    print("📈 QUARTERLY BTW BREAKDOWN")
    print("="*60)
    
    cursor = conn.cursor()
    current_year = str(date.today().year)
    
    cursor.execute("""
        SELECT 
            CASE 
                WHEN CAST(substr(InvoiceDate, 4, 2) AS INTEGER) IN (1,2,3) THEN 'Q1'
                WHEN CAST(substr(InvoiceDate, 4, 2) AS INTEGER) IN (4,5,6) THEN 'Q2'
                WHEN CAST(substr(InvoiceDate, 4, 2) AS INTEGER) IN (7,8,9) THEN 'Q3'
                ELSE 'Q4'
            END as quarter,
            COUNT(*) as invoices_count,
            SUM(Excl) as total_excl,
            SUM(BTW) as total_btw,
            SUM(Incl) as total_incl
        FROM Invoices
        WHERE (status IS NULL OR status = 'active') 
        AND substr(InvoiceDate, 7, 4) = ?
        GROUP BY quarter
        ORDER BY quarter
    """, (current_year,))
    
    quarters = cursor.fetchall()
    
    print(f"Quarterly breakdown for {current_year}:")
    print("-" * 70)
    print(f"{'Quarter':<10} {'Invoices':<10} {'Excl Total':<12} {'BTW Total':<12} {'Incl Total':<12}")
    print("-" * 70)
    
    yearly_total_btw = 0
    for quarter in quarters:
        q = quarter['quarter']
        count = quarter['invoices_count']
        excl = quarter['total_excl'] or 0
        btw = quarter['total_btw'] or 0
        incl = quarter['total_incl'] or 0
        
        yearly_total_btw += btw
        print(f"{q:<10} {count:<10} €{excl:<11.2f} €{btw:<11.2f} €{incl:<11.2f}")
    
    print("-" * 70)
    print(f"💰 Yearly Total BTW: €{yearly_total_btw:.2f}")
    
    return yearly_total_btw

def check_binned_invoices_impact(conn):
    """Check how much BTW is in binned invoices"""
    print("\n" + "="*60)
    print("🗑️  BINNED INVOICES IMPACT")
    print("="*60)
    
    cursor = conn.cursor()
    current_year = str(date.today().year)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as count,
            SUM(BTW) as total_btw,
            SUM(Excl) as total_excl,
            SUM(Incl) as total_incl
        FROM Invoices 
        WHERE status = 'binned'
        AND substr(InvoiceDate, 7, 4) = ?
    """, (current_year,))
    
    binned_data = cursor.fetchone()
    
    if binned_data and binned_data['count'] > 0:
        count = binned_data['count']
        btw = binned_data['total_btw'] or 0
        excl = binned_data['total_excl'] or 0
        incl = binned_data['total_incl'] or 0
        
        print(f"Binned invoices from {current_year}:")
        print(f"📊 Count: {count}")
        print(f"💰 BTW Total: €{btw:.2f}")
        print(f"💰 Excl Total: €{excl:.2f}")
        print(f"💰 Incl Total: €{incl:.2f}")
        
        if btw > 0:
            print(f"\n⚠️  WARNING: €{btw:.2f} BTW is excluded due to binned status!")
            return btw
    else:
        print(f"✅ No binned invoices found for {current_year}")
        return 0

def detailed_invoice_list(conn, limit=20):
    """Show detailed list of recent invoices for manual verification"""
    print("\n" + "="*60)
    print(f"📋 RECENT INVOICES DETAILS (Last {limit})")
    print("="*60)
    
    cursor = conn.cursor()
    current_year = str(date.today().year)
    
    cursor.execute("""
        SELECT 
            InvoiceID,
            InvoiceDate,
            Excl,
            BTW,
            Incl,
            status,
            ROUND(Excl * 0.21, 2) as calculated_btw
        FROM Invoices 
        WHERE substr(InvoiceDate, 7, 4) = ?
        ORDER BY CAST(InvoiceID AS INTEGER) DESC
        LIMIT ?
    """, (current_year, limit))
    
    invoices = cursor.fetchall()
    
    print("-" * 100)
    print(f"{'Invoice':<10} {'Date':<12} {'Status':<10} {'Excl':<10} {'BTW':<10} {'Calc BTW':<10} {'Incl':<10} {'Match':<8}")
    print("-" * 100)
    
    for invoice in invoices:
        invoice_id = invoice['InvoiceID']
        date_str = invoice['InvoiceDate']
        status = invoice['status'] or 'NULL'
        excl = invoice['Excl'] or 0
        btw = invoice['BTW'] or 0
        incl = invoice['Incl'] or 0
        calc_btw = invoice['calculated_btw'] or 0
        
        match = "✅" if abs(btw - calc_btw) <= 0.01 else "❌"
        included = "✅" if status in [None, 'active'] else "❌"
        
        print(f"{invoice_id:<10} {date_str:<12} {status:<10} €{excl:<9.2f} €{btw:<9.2f} €{calc_btw:<9.2f} €{incl:<9.2f} {match:<8}")

def summary_analysis():
    """Provide summary and recommendations"""
    print("\n" + "="*60)
    print("📊 SUMMARY & RECOMMENDATIONS")
    print("="*60)
    
    print("""
To identify the €50.92 difference (€432 - €381.08), check:

1. 🔍 INVOICE STATUS: Ensure all relevant invoices have status NULL or 'active'
2. 📅 DATE RANGE: Verify you're looking at the correct year/period  
3. 🧮 CALCULATIONS: Check if stored BTW matches calculated BTW (21% of Excl)
4. 🗑️  BINNED INVOICES: Check if important invoices were accidentally binned
5. 🔢 ROUNDING: Look for rounding discrepancies in BTW calculations

NEXT STEPS:
- Review invoices with status other than NULL/'active'
- Check for any invoices with incorrect BTW calculations
- Verify no important invoices are marked as 'binned'
- Consider if you need invoices from multiple years
    """)

def main():
    """Main diagnostic function"""
    print("🔍 BTW CALCULATION DIAGNOSTIC TOOL")
    print("=" * 60)
    print("This script will analyze your invoice database to identify")
    print("discrepancies in BTW calculations.")
    print("=" * 60)
    
    # Connect to database
    conn = connect_to_database()
    if not conn:
        return
    
    try:
        # Run all diagnostic checks
        active_btw = check_invoice_statuses(conn)
        current_year_btw = check_date_ranges(conn)
        stored_btw, calculated_btw = check_btw_calculation_accuracy(conn)
        quarterly_btw = check_quarterly_breakdown(conn)
        binned_btw = check_binned_invoices_impact(conn)
        detailed_invoice_list(conn)
        
        # Final summary
        print("\n" + "="*60)
        print("🎯 FINAL COMPARISON")
        print("="*60)
        print(f"Expected BTW (manual):     €432.00")
        print(f"Calculated BTW (app):      €381.08")
        print(f"Difference:                €{432.00 - 381.08:.2f}")
        print()
        print(f"Database active BTW:       €{active_btw:.2f}")
        print(f"Current year BTW:          €{current_year_btw:.2f}")
        print(f"Quarterly sum BTW:         €{quarterly_btw:.2f}")
        print(f"Binned BTW (excluded):     €{binned_btw:.2f}")
        print()
        
        if binned_btw > 0:
            total_including_binned = current_year_btw + binned_btw
            print(f"💡 Including binned:        €{total_including_binned:.2f}")
            
            if abs(total_including_binned - 432.00) < 1.0:
                print("🎯 LIKELY SOLUTION: Some invoices are marked as 'binned' that should be included!")
        
        summary_analysis()
        
    finally:
        conn.close()

if __name__ == "__main__":
    main()
