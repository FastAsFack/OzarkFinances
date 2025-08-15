"""
Ozark Finances Flask Application
A web port of the AutoHotkey finance management application
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import sqlite3
import os
from datetime import datetime
import csv
import openpyxl
from pathlib import Path
import logging
from config import config

# Import the invoice generator integration
from invoice_generator_integration import register_invoice_generator

app = Flask(__name__)

# Load configuration
config_name = os.environ.get('FLASK_CONFIG') or 'default'
app.config.from_object(config[config_name])
config[config_name].init_app(app)

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Register the invoice generator integration
register_invoice_generator(app)

class DatabaseManager:
    def __init__(self, db_path):
        self.db_path = db_path
        
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def execute_query(self, query, params=None):
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()
    
    def execute_update(self, query, params=None):
        """Execute an update/insert/delete query"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            conn.commit()
            return cursor.rowcount

db_manager = DatabaseManager(app.config['DATABASE_PATH'])

def format_euro(amount):
    """Format amount as Euro currency"""
    return f"€{amount:,.2f}"

def parse_euro(euro_str):
    """Parse Euro string back to float"""
    return float(euro_str.replace('€', '').replace(',', ''))

@app.route('/')
def index():
    """Main dashboard with comprehensive statistics"""
    try:
        # Get invoice statistics
        invoice_stats = db_manager.execute_query("""
            SELECT 
                COUNT(*) as total_invoices,
                SUM(Incl) as total_amount,
                AVG(Incl) as avg_amount,
                MAX(Incl) as max_amount,
                MIN(Incl) as min_amount
            FROM Invoices
        """)[0]
        
        # Get recent invoices (last 5)
        recent_invoices = db_manager.execute_query("""
            SELECT InvoiceID, InvoiceDate, Incl 
            FROM Invoices 
            ORDER BY CAST(InvoiceID AS INTEGER) DESC 
            LIMIT 5
        """)
        
        # Get withdraw statistics
        withdraw_stats = db_manager.execute_query("""
            SELECT 
                COUNT(*) as total_withdraws,
                SUM(Amount) as total_amount,
                AVG(Amount) as avg_amount
            FROM Withdraw
        """)[0]
        
        # Get recent withdraws (last 5)
        recent_withdraws = db_manager.execute_query("""
            SELECT Date, Amount 
            FROM Withdraw 
            ORDER BY Date DESC 
            LIMIT 5
        """)
        
        # Get debt statistics
        debt_stats = db_manager.execute_query("""
            SELECT 
                COUNT(*) as total_debts,
                SUM(Amount) as total_debt_amount,
                SUM(OriginalDebt) as original_debt_amount
            FROM DebtRegister
        """)[0]
        
        # Get all debts for display
        all_debts = db_manager.execute_query("""
            SELECT DebtName, Amount, OriginalDebt 
            FROM DebtRegister 
            ORDER BY Amount DESC
        """)
        
        # Get quarterly data count
        quarterly_info = db_manager.execute_query("""
            SELECT COUNT(*) as total_quarters
            FROM KwartaalData
        """)[0]
        
        return render_template('index.html',
                             invoice_stats=invoice_stats,
                             recent_invoices=recent_invoices,
                             withdraw_stats=withdraw_stats,
                             recent_withdraws=recent_withdraws,
                             debt_stats=debt_stats,
                             all_debts=all_debts,
                             quarterly_info=quarterly_info,
                             format_euro=format_euro)
                             
    except Exception as e:
        print(f"Error in dashboard: {e}")
        # Return basic template without data on error
        return render_template('index.html', 
                             error="Failed to load dashboard data",
                             format_euro=format_euro)

@app.route('/invoices')
def invoices():
    """Invoice management page with comprehensive filtering"""
    # Get all filter parameters
    invoice_number = request.args.get('invoice_number', '')
    invoice_number_startswith = request.args.get('invoice_number_startswith', '')
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    exact_date = request.args.get('exact_date', '')
    month_filter = request.args.get('month_filter', '')
    year_filter = request.args.get('year_filter', '')
    quarter_filter = request.args.get('quarter_filter', '')
    weekday_filter = request.args.getlist('weekday_filter')
    date_preset = request.args.get('date_preset', '')
    page = request.args.get('page', 1, type=int)
    per_page = 50  # Items per page
    
    try:
        from datetime import datetime, timedelta
        
        # Handle date presets
        if date_preset:
            today = datetime.now()
            if date_preset == 'this_month':
                date_from = today.replace(day=1).strftime('%Y-%m-%d')
                date_to = today.strftime('%Y-%m-%d')
            elif date_preset == 'last_month':
                first_day_this_month = today.replace(day=1)
                last_day_last_month = first_day_this_month - timedelta(days=1)
                first_day_last_month = last_day_last_month.replace(day=1)
                date_from = first_day_last_month.strftime('%Y-%m-%d')
                date_to = last_day_last_month.strftime('%Y-%m-%d')
            elif date_preset == 'this_quarter':
                quarter = (today.month - 1) // 3 + 1
                first_month = (quarter - 1) * 3 + 1
                date_from = today.replace(month=first_month, day=1).strftime('%Y-%m-%d')
                date_to = today.strftime('%Y-%m-%d')
            elif date_preset == 'this_year':
                date_from = today.replace(month=1, day=1).strftime('%Y-%m-%d')
                date_to = today.strftime('%Y-%m-%d')
        
        # Build base query with weekday calculation (FIXED for DD-MM-YYYY format)
        base_query = """
        SELECT InvoiceID, InvoiceDate, Excl, BTW, Incl,
               substr(InvoiceDate, 4, 2) as Month,
               substr(InvoiceDate, 7, 4) as Year,
               CASE 
                   WHEN CAST(substr(InvoiceDate, 4, 2) AS INTEGER) IN (1,2,3) THEN 'Q1'
                   WHEN CAST(substr(InvoiceDate, 4, 2) AS INTEGER) IN (4,5,6) THEN 'Q2'
                   WHEN CAST(substr(InvoiceDate, 4, 2) AS INTEGER) IN (7,8,9) THEN 'Q3'
                   ELSE 'Q4'
               END as Quarter,
               CASE strftime('%w', substr(InvoiceDate, 7, 4) || '-' || substr(InvoiceDate, 4, 2) || '-' || substr(InvoiceDate, 1, 2))
                   WHEN '0' THEN 'Sunday'
                   WHEN '1' THEN 'Monday'
                   WHEN '2' THEN 'Tuesday'
                   WHEN '3' THEN 'Wednesday'
                   WHEN '4' THEN 'Thursday'
                   WHEN '5' THEN 'Friday'
                   WHEN '6' THEN 'Saturday'
               END as Weekday
        FROM Invoices
        """
        
        count_query = "SELECT COUNT(*) as total FROM Invoices"
        params = []
        
        where_conditions = []
        
        # Invoice number filters
        if invoice_number:
            where_conditions.append("InvoiceID = ?")
            params.append(invoice_number)
        
        if invoice_number_startswith:
            where_conditions.append("InvoiceID LIKE ?")
            params.append(f"{invoice_number_startswith}%")
        
        # Date filters (FIXED for DD-MM-YYYY format)
        if exact_date:
            # Convert YYYY-MM-DD input to DD-MM-YYYY for comparison
            try:
                date_parts = exact_date.split('-')  # YYYY-MM-DD
                formatted_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"  # DD-MM-YYYY
                where_conditions.append("InvoiceDate = ?")
                params.append(formatted_date)
            except:
                pass  # Skip invalid date format
        elif date_from or date_to:
            if date_from:
                # Convert YYYY-MM-DD to DD-MM-YYYY for comparison
                try:
                    date_parts = date_from.split('-')
                    formatted_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
                    # For date comparison with DD-MM-YYYY, we need to convert to comparable format
                    where_conditions.append("date(substr(InvoiceDate, 7, 4) || '-' || substr(InvoiceDate, 4, 2) || '-' || substr(InvoiceDate, 1, 2)) >= date(?)")
                    params.append(date_from)
                except:
                    pass
            if date_to:
                try:
                    date_parts = date_to.split('-')
                    formatted_date = f"{date_parts[2]}-{date_parts[1]}-{date_parts[0]}"
                    where_conditions.append("date(substr(InvoiceDate, 7, 4) || '-' || substr(InvoiceDate, 4, 2) || '-' || substr(InvoiceDate, 1, 2)) <= date(?)")
                    params.append(date_to)
                except:
                    pass
        
        # Time-based filters (FIXED for DD-MM-YYYY format)
        if month_filter:
            where_conditions.append("substr(InvoiceDate, 4, 2) = ?")
            params.append(month_filter.zfill(2))
            
        if year_filter:
            where_conditions.append("substr(InvoiceDate, 7, 4) = ?")
            params.append(year_filter)
            
        if quarter_filter:
            if quarter_filter == 'Q1':
                where_conditions.append("CAST(substr(InvoiceDate, 4, 2) AS INTEGER) IN (1,2,3)")
            elif quarter_filter == 'Q2':
                where_conditions.append("CAST(substr(InvoiceDate, 4, 2) AS INTEGER) IN (4,5,6)")
            elif quarter_filter == 'Q3':
                where_conditions.append("CAST(substr(InvoiceDate, 4, 2) AS INTEGER) IN (7,8,9)")
            elif quarter_filter == 'Q4':
                where_conditions.append("CAST(substr(InvoiceDate, 4, 2) AS INTEGER) IN (10,11,12)")
        
        # Weekday filter (FIXED for DD-MM-YYYY format)
        if weekday_filter:
            weekday_conditions = []
            for day in weekday_filter:
                day_num = {'Sunday': '0', 'Monday': '1', 'Tuesday': '2', 'Wednesday': '3', 
                          'Thursday': '4', 'Friday': '5', 'Saturday': '6'}.get(day)
                if day_num:
                    # Convert DD-MM-YYYY to YYYY-MM-DD for strftime
                    weekday_conditions.append(f"strftime('%w', substr(InvoiceDate, 7, 4) || '-' || substr(InvoiceDate, 4, 2) || '-' || substr(InvoiceDate, 1, 2)) = '{day_num}'")
            if weekday_conditions:
                where_conditions.append(f"({' OR '.join(weekday_conditions)})")
        
        if where_conditions:
            where_clause = " WHERE " + " AND ".join(where_conditions)
            base_query += where_clause
            count_query += where_clause
        
        # Get total count for pagination
        total_result = db_manager.execute_query(count_query, params)
        total_items = total_result[0]['total'] if total_result else 0
        
        # Calculate pagination
        total_pages = (total_items + per_page - 1) // per_page
        offset = (page - 1) * per_page
        has_prev = page > 1
        has_next = page < total_pages
        prev_num = page - 1 if has_prev else None
        next_num = page + 1 if has_next else None
        
        # Build final query with pagination
        query = base_query + " ORDER BY CAST(InvoiceID AS INTEGER) DESC LIMIT ? OFFSET ?"
        params.extend([per_page, offset])
        
        invoices_data = db_manager.execute_query(query, params)
        
        # Calculate totals (for all filtered items, not just current page)
        totals_query = "SELECT SUM(Excl) as total_excl, SUM(BTW) as total_btw, SUM(Incl) as total_incl FROM Invoices"
        if where_conditions:
            totals_query += " WHERE " + " AND ".join(where_conditions)
        
        totals_result = db_manager.execute_query(totals_query, params[:-2])  # Remove LIMIT and OFFSET params
        totals = totals_result[0] if totals_result else {'total_excl': 0, 'total_btw': 0, 'total_incl': 0}
        
        # Get available years and months for dropdowns (FIXED for DD-MM-YYYY format)
        years_query = "SELECT DISTINCT substr(InvoiceDate,7,4) as year FROM Invoices ORDER BY year DESC"
        available_years = [row['year'] for row in db_manager.execute_query(years_query)]
        
        months_query = "SELECT DISTINCT substr(InvoiceDate,4,2) as month FROM Invoices ORDER BY CAST(month AS INTEGER)"
        available_months = [row['month'] for row in db_manager.execute_query(months_query)]
        
        # Create pagination object
        pagination = {
            'page': page,
            'per_page': per_page,
            'total': total_items,
            'total_pages': total_pages,
            'has_prev': has_prev,
            'has_next': has_next,
            'prev_num': prev_num,
            'next_num': next_num
        }
        
        return render_template('invoices.html', 
                             invoices=invoices_data,
                             pagination=pagination,
                             total_excl=totals['total_excl'] or 0,
                             total_btw=totals['total_btw'] or 0,
                             total_incl=totals['total_incl'] or 0,
                             # All filter parameters
                             invoice_number=invoice_number,
                             invoice_number_startswith=invoice_number_startswith,
                             date_from=date_from,
                             date_to=date_to,
                             exact_date=exact_date,
                             month_filter=month_filter,
                             year_filter=year_filter,
                             quarter_filter=quarter_filter,
                             weekday_filter=weekday_filter,
                             date_preset=date_preset,
                             available_years=available_years,
                             available_months=available_months,
                             format_euro=format_euro)
                             
    except Exception as e:
        print(f"Error in invoices route: {e}")
        return render_template('invoices.html', 
                             invoices=[],
                             pagination=None,
                             total_excl=0,
                             total_btw=0,
                             total_incl=0,
                             # Empty filter parameters for error case
                             invoice_number='',
                             invoice_number_startswith='',
                             date_from='',
                             date_to='',
                             exact_date='',
                             month_filter='',
                             year_filter='',
                             quarter_filter='',
                             weekday_filter=[],
                             date_preset='',
                             available_years=[],
                             available_months=[],
                             format_euro=format_euro,
                             error="Failed to load invoice data")

@app.route('/withdraws')
def withdraws():
    """Withdraw management page"""
    try:
        # Get pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)  # Show 50 entries per page
        
        # Get total count for pagination
        total_count = db_manager.execute_query("SELECT COUNT(*) as count FROM Withdraw")[0]['count']
        
        # Calculate offset
        offset = (page - 1) * per_page
        
        # Get paginated withdraws data
        withdraws_data = db_manager.execute_query(
            "SELECT Date, Amount FROM Withdraw ORDER BY Date DESC LIMIT ? OFFSET ?", 
            (per_page, offset)
        )
        
        # Calculate totals (from all records, not just current page)
        all_withdraws = db_manager.execute_query("SELECT Amount FROM Withdraw")
        total_rows = len(all_withdraws)
        total_amount = sum(abs(withdraw['Amount']) for withdraw in all_withdraws) if all_withdraws else 0
        
        # Get most recent date
        recent_data = db_manager.execute_query("SELECT Date FROM Withdraw ORDER BY Date DESC LIMIT 1")
        recent_date = recent_data[0]['Date'] if recent_data else None
        
        # Calculate pagination info
        total_pages = (total_count + per_page - 1) // per_page
        has_prev = page > 1
        has_next = page < total_pages
        
        return render_template('withdraws.html',
                             withdraws=withdraws_data,
                             total_rows=total_rows,
                             total_amount=total_amount,
                             recent_date=recent_date,
                             format_euro=format_euro,
                             pagination={
                                 'page': page,
                                 'per_page': per_page,
                                 'total': total_count,
                                 'total_pages': total_pages,
                                 'has_prev': has_prev,
                                 'has_next': has_next,
                                 'prev_num': page - 1 if has_prev else None,
                                 'next_num': page + 1 if has_next else None
                             })
    except Exception as e:
        logger.error(f"Error loading withdraws: {e}")
        flash(f'Error loading withdraws: {str(e)}', 'error')
        return render_template('withdraws.html',
                             withdraws=[],
                             total_rows=0,
                             total_amount=0,
                             recent_date=None,
                             format_euro=format_euro,
                             pagination={
                                 'page': 1,
                                 'per_page': 50,
                                 'total': 0,
                                 'total_pages': 0,
                                 'has_prev': False,
                                 'has_next': False,
                                 'prev_num': None,
                                 'next_num': None
                             })

@app.route('/withdraws/add', methods=['POST'])
def add_withdraw():
    """Add a new withdraw entry"""
    try:
        date = request.form.get('date')
        amount = float(request.form.get('amount'))
        
        # Make amount negative for withdraw
        if amount > 0:
            amount = -amount
        
        db_manager.execute_update(
            "INSERT INTO Withdraw (Date, Amount) VALUES (?, ?)",
            (date, amount)
        )
        
        flash('Withdraw added successfully', 'success')
    except Exception as e:
        logger.error(f"Error adding withdraw: {e}")
        flash(f'Error adding withdraw: {str(e)}', 'error')
    
    return redirect(url_for('withdraws'))

@app.route('/withdraws/upload', methods=['POST'])
def upload_withdraws():
    """Upload withdraws from CSV file"""
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(url_for('withdraws'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(url_for('withdraws'))
    
    if file and file.filename.endswith('.csv'):
        try:
            # Read CSV content
            content = file.read().decode('utf-8')
            lines = content.strip().split('\n')
            
            inserted_count = 0
            for line in lines:
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 2:
                        date = parts[0].strip()
                        amount = float(parts[1].strip())
                        
                        db_manager.execute_update(
                            "INSERT INTO Withdraw (Date, Amount) VALUES (?, ?)",
                            (date, amount)
                        )
                        inserted_count += 1
            
            flash(f'Successfully imported {inserted_count} withdraw entries', 'success')
        except Exception as e:
            logger.error(f"Error uploading withdraws: {e}")
            flash(f'Error processing file: {str(e)}', 'error')
    else:
        flash('Please upload a CSV file', 'error')
    
    return redirect(url_for('withdraws'))

@app.route('/withdraws/delete/<int:row_id>', methods=['POST'])
def delete_withdraw(row_id):
    """Delete a withdraw entry"""
    date = request.form.get('date')
    amount = request.form.get('amount')
    
    db_manager.execute_update(
        "DELETE FROM Withdraw WHERE Date = ? AND Amount = ?",
        (date, amount)
    )
    
    flash('Withdraw deleted successfully', 'success')
    return redirect(url_for('withdraws'))

@app.route('/important-info')
def important_info():
    """Important quarterly information page"""
    try:
        kwartaal_data = db_manager.execute_query(
            "SELECT tijdvak, betaling, kenmerk, betaald, Amount FROM KwartaalData"
        )
        
        return render_template('important_info.html',
                             kwartaal_data=kwartaal_data,
                             format_euro=format_euro)
    except Exception as e:
        logger.error(f"Error loading important info: {e}")
        flash(f'Error loading important info: {str(e)}', 'error')
        return render_template('important_info.html',
                             kwartaal_data=[],
                             format_euro=format_euro)

@app.route('/important-info/toggle/<kenmerk>', methods=['POST'])
def toggle_kwartaal_state(kenmerk):
    """Toggle the payment state of a quarterly item"""
    try:
        current_state = db_manager.execute_query(
            "SELECT betaald FROM KwartaalData WHERE kenmerk = ?", (kenmerk,)
        )
        
        if current_state:
            new_state = "No" if current_state[0]['betaald'] == "Yes" else "Yes"
            db_manager.execute_update(
                "UPDATE KwartaalData SET betaald = ? WHERE kenmerk = ?",
                (new_state, kenmerk)
            )
            flash(f'Payment state updated to {new_state}', 'success')
        else:
            flash('Item not found', 'error')
    except Exception as e:
        logger.error(f"Error toggling state: {e}")
        flash(f'Error updating payment state: {str(e)}', 'error')
    
    return redirect(url_for('important_info'))

@app.route('/debt')
def debt():
    """Debt management page"""
    debt_data = db_manager.execute_query(
        "SELECT DebtName, Amount, OriginalDebt FROM DebtRegister"
    )
    
    return render_template('debt.html',
                         debt_data=debt_data,
                         format_euro=format_euro)

@app.route('/debt/add', methods=['POST'])
def add_debt():
    """Add a new debt"""
    debt_name = request.form.get('debt_name')
    amount = float(request.form.get('amount'))
    
    # Create debt database file
    debt_db_path = app.config['DATA_DIR'] / f"{debt_name}.sqlite"
    
    with sqlite3.connect(debt_db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS DebtSource (
                Amount REAL NOT NULL,
                CreatedDate TEXT NOT NULL,
                UNIX INTEGER NOT NULL
            )
        """)
    
    # Add to main register
    unix_timestamp = int(datetime.now().timestamp())
    db_manager.execute_update(
        "INSERT INTO DebtRegister (DebtName, Amount, UnixStamp, OriginalDebt) VALUES (?, ?, ?, ?)",
        (debt_name, amount, unix_timestamp, amount)
    )
    
    flash('Debt added successfully', 'success')
    return redirect(url_for('debt'))

@app.route('/debt/update/<debt_name>', methods=['POST'])
def update_debt(debt_name):
    """Update debt amount (payment)"""
    payment_amount = float(request.form.get('payment_amount'))
    
    # Get current debt amount
    current_debt = db_manager.execute_query(
        "SELECT Amount FROM DebtRegister WHERE DebtName = ?", (debt_name,)
    )
    
    if current_debt:
        new_amount = current_debt[0]['Amount'] - payment_amount
        
        # Update main register
        db_manager.execute_update(
            "UPDATE DebtRegister SET Amount = ? WHERE DebtName = ?",
            (new_amount, debt_name)
        )
        
        # Add payment record to debt database
        debt_db_path = app.config['DATA_DIR'] / f"{debt_name}.sqlite"
        if debt_db_path.exists():
            with sqlite3.connect(debt_db_path) as conn:
                conn.execute(
                    "INSERT INTO DebtSource (Amount, CreatedDate, UNIX) VALUES (?, ?, ?)",
                    (payment_amount, datetime.now().strftime('%d/%m/%Y'), int(datetime.now().timestamp()))
                )
        
        flash(f'Payment of {format_euro(payment_amount)} recorded', 'success')
    
    return redirect(url_for('debt'))

@app.route('/debt/log/<debt_name>')
def debt_log(debt_name):
    """View debt payment log"""
    debt_db_path = app.config['DATA_DIR'] / f"{debt_name}.sqlite"
    
    if not debt_db_path.exists():
        flash('Debt log not found', 'error')
        return redirect(url_for('debt'))
    
    with sqlite3.connect(debt_db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("SELECT CreatedDate, Amount FROM DebtSource ORDER BY UNIX DESC")
        log_data = cursor.fetchall()
    
    return render_template('debt_log.html',
                         debt_name=debt_name,
                         log_data=log_data,
                         format_euro=format_euro)

@app.route('/api/invoices/scan', methods=['POST'])
def scan_invoices():
    """API endpoint to scan for new invoices (placeholder)"""
    # This would implement the Excel scanning functionality
    # For now, return a placeholder response
    return jsonify({'status': 'success', 'message': 'Scan functionality not yet implemented'})

@app.route('/card-variations')
def card_variations():
    """Display different card design variations"""
    return render_template('card_variations.html')

@app.context_processor
def utility_processor():
    """Make utility functions available in templates"""
    return dict(
        format_euro=format_euro,
        today=datetime.now().strftime('%Y-%m-%d')
    )

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])
