"""
Invoice Generator Popup Integration Module
Handles integration between Flask app and external invoice generator via popup window
"""

from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from datetime import datetime
import json
import sqlite3
import os

# Create blueprint for invoice generator integration
invoice_generator_bp = Blueprint('invoice_generator', __name__)

def get_db_connection():
    """Get database connection using the same pattern as main app"""
    from pathlib import Path
    import os
    
    # Use the same database path as the main app
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or os.path.abspath('../data/FinanceData.sqlite')
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@invoice_generator_bp.route('/create-invoice-popup')
def create_invoice_popup():
    """
    Route to display the invoice creation page with popup integration
    This page contains the button to open the invoice generator popup
    """
    return render_template('invoice_generator_popup.html')

@invoice_generator_bp.route('/api/receive-invoice', methods=['POST'])
def receive_invoice_data():
    """
    API endpoint to receive invoice data from the popup window
    Expected JSON format:
    {
        "invoice_number": "INV-001",
        "client_name": "Client Name",
        "client_email": "client@email.com", 
        "client_address": "123 Main St",
        "date": "2025-01-15",
        "due_date": "2025-02-15",
        "items": [
            {
                "description": "Service/Product",
                "quantity": 1,
                "rate": 100.00,
                "amount": 100.00
            }
        ],
        "subtotal": 100.00,
        "tax_rate": 8.25,
        "tax_amount": 8.25,
        "total": 108.25,
        "notes": "Additional notes",
        "status": "draft"
    }
    """
    try:
        # Get JSON data from the request
        invoice_data = request.get_json()
        
        if not invoice_data:
            return jsonify({'error': 'No invoice data received'}), 400
        
        # Validate required fields
        required_fields = ['invoice_number', 'client_name', 'date', 'total']
        for field in required_fields:
            if field not in invoice_data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Save invoice to database
        invoice_id = save_invoice_to_database(invoice_data)
        
        return jsonify({
            'success': True, 
            'invoice_id': invoice_id,
            'message': 'Invoice saved successfully'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error saving invoice: {str(e)}'}), 500

def save_invoice_to_database(invoice_data):
    """
    Save invoice data to the database using the existing Invoices table schema
    Returns the InvoiceID of the created invoice
    """
    conn = get_db_connection()
    try:
        # Convert invoice data to match existing schema
        invoice_id = invoice_data.get('invoice_number', 'INV-000')
        invoice_date = invoice_data.get('date', datetime.now().strftime('%d-%m-%Y'))
        
        # Calculate amounts from the invoice data
        subtotal = float(invoice_data.get('subtotal', 0))
        tax_amount = float(invoice_data.get('tax_amount', 0))
        total = float(invoice_data.get('total', subtotal + tax_amount))
        
        # If we have tax info, calculate Excl and BTW
        if tax_amount > 0:
            excl = subtotal  # Amount excluding tax
            btw = tax_amount  # Tax amount
            incl = total     # Amount including tax
        else:
            # If no tax info, assume total is including tax and calculate backwards
            # Using standard 21% BTW rate as default
            incl = total
            excl = total / 1.21
            btw = incl - excl
        
        # Convert date format from YYYY-MM-DD to DD-MM-YYYY if needed
        if '-' in invoice_date and len(invoice_date.split('-')[0]) == 4:
            # Convert from YYYY-MM-DD to DD-MM-YYYY
            parts = invoice_date.split('-')
            invoice_date = f"{parts[2]}-{parts[1]}-{parts[0]}"
        
        # Insert into the existing Invoices table
        cursor = conn.execute('''
            INSERT INTO Invoices (InvoiceID, InvoiceDate, Excl, BTW, Incl)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            invoice_id,
            invoice_date,
            round(excl, 2),
            round(btw, 2),
            round(incl, 2)
        ))
        
        conn.commit()
        return invoice_id
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

@invoice_generator_bp.route('/api/invoice-generator-config')
def get_invoice_generator_config():
    """
    API endpoint to provide configuration data to the invoice generator
    This can include company info, next invoice number, etc.
    """
    try:
        conn = get_db_connection()
        
        # Get next invoice number
        cursor = conn.execute('SELECT MAX(invoice_number) as last_number FROM invoices')
        result = cursor.fetchone()
        
        # Generate next invoice number (simple increment logic)
        last_number = result['last_number'] if result['last_number'] else 'INV-000'
        next_number = generate_next_invoice_number(last_number)
        
        # Company/app configuration (this could come from settings later)
        config = {
            'next_invoice_number': next_number,
            'company_name': 'Ozark Finances',
            'default_tax_rate': 8.25,
            'currency_symbol': '$',
            'date_format': 'YYYY-MM-DD'
        }
        
        conn.close()
        return jsonify(config)
        
    except Exception as e:
        return jsonify({'error': f'Error getting config: {str(e)}'}), 500

def generate_next_invoice_number(last_number):
    """
    Generate the next invoice number based on the last one
    Simple increment logic - can be enhanced later
    """
    try:
        if last_number and last_number.startswith('INV-'):
            # Extract number part and increment
            number_part = int(last_number.split('-')[1])
            return f'INV-{number_part + 1:03d}'
        else:
            # Start with INV-001 if no previous invoices
            return 'INV-001'
    except:
        return 'INV-001'

@invoice_generator_bp.route('/invoices-list')
def invoices_list():
    """
    Display list of all invoices including those created via popup
    Enhanced version of the existing invoices page
    """
    conn = get_db_connection()
    
    # Get invoices with optional status filter
    status_filter = request.args.get('status', '')
    
    if status_filter:
        invoices = conn.execute('''
            SELECT * FROM invoices 
            WHERE status = ? 
            ORDER BY created_at DESC
        ''', (status_filter,)).fetchall()
    else:
        invoices = conn.execute('''
            SELECT * FROM invoices 
            ORDER BY created_at DESC
        ''').fetchall()
    
    conn.close()
    
    return render_template('invoices_list_enhanced.html', 
                         invoices=invoices, 
                         current_status=status_filter)

# Database initialization functions
def init_invoice_tables():
    """
    Initialize database tables for invoice functionality
    Run this once to set up the required tables
    """
    conn = get_db_connection()
    
    # Create invoices table
    conn.execute('''
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT UNIQUE NOT NULL,
            client_name TEXT NOT NULL,
            client_email TEXT,
            client_address TEXT,
            invoice_date DATE NOT NULL,
            due_date DATE,
            subtotal DECIMAL(10,2) DEFAULT 0,
            tax_rate DECIMAL(5,2) DEFAULT 0,
            tax_amount DECIMAL(10,2) DEFAULT 0,
            total_amount DECIMAL(10,2) NOT NULL,
            notes TEXT,
            status TEXT DEFAULT 'draft',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create invoice_items table for line items
    conn.execute('''
        CREATE TABLE IF NOT EXISTS invoice_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            quantity DECIMAL(10,2) DEFAULT 1,
            rate DECIMAL(10,2) DEFAULT 0,
            amount DECIMAL(10,2) DEFAULT 0,
            FOREIGN KEY (invoice_id) REFERENCES invoices (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Invoice tables initialized successfully!")

# Helper function to register this blueprint with the main app
def register_invoice_generator(app):
    """
    Register the invoice generator blueprint with the Flask app
    Call this from your main app.py file
    """
    app.register_blueprint(invoice_generator_bp, url_prefix='/invoice-generator')
    
    # Initialize tables if they don't exist
    with app.app_context():
        init_invoice_tables()
