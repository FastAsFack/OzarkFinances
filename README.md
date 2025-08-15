# Ozark Finances Flask Port

A Flask web application port of the AutoHotkey-based Ozark Finances system. This application provides a modern web interface for managing invoices, tracking withdrawals, monitoring quarterly information, and handling debt management.

## Features

### 📊 Invoice Management
- View and filter invoices by year and series
- Calculate totals (Excl BTW, BTW, Incl BTW)
- Scan for new invoices functionality
- Modern table interface with sorting and filtering

### 💰 Withdraw Tracking
- Add withdrawals manually or via CSV upload
- View withdrawal history with totals
- Track total amount withdrawn and recent activity
- Delete individual withdrawal entries

### ℹ️ Important Quarterly Information
- View quarterly payment data (Tijdvak, Betaling, Kenmerk)
- Toggle payment status between "Paid" and "Unpaid"
- Visual status indicators

### 🏦 Debt Management
- Add new debts with original amounts
- Track payment progress with visual progress bars
- Record payments and maintain payment logs
- View detailed payment history for each debt

## Installation

1. **Clone or download the FlaskPort folder**

2. **Install Python dependencies:**
   ```cmd
   pip install -r requirements.txt
   ```

3. **Ensure your SQLite database is accessible:**
   - The application expects the database at `../data/FinanceData.sqlite`
   - Update the `DATABASE_PATH` in `app.py` if your database is located elsewhere

4. **Run the application:**
   ```cmd
   python app.py
   ```

5. **Access the application:**
   - Open your web browser and go to `http://localhost:5000`

## Configuration

### Database Path
Update the database path in `app.py`:
```python
DATABASE_PATH = 'path/to/your/FinanceData.sqlite'
```

### Secret Key
For production use, change the secret key in `app.py`:
```python
app.secret_key = 'your-secure-secret-key-here'
```

## Database Schema Expected

The application expects the following SQLite tables:

### Invoices
```sql
CREATE TABLE Invoices (
    InvoiceID TEXT,
    InvoiceDate TEXT,
    Excl REAL,
    BTW REAL,
    Incl REAL
);
```

### Withdraw
```sql
CREATE TABLE Withdraw (
    Date TEXT,
    Amount REAL
);
```

### KwartaalData
```sql
CREATE TABLE KwartaalData (
    tijdvak TEXT,
    betaling TEXT,
    kenmerk TEXT,
    betaald TEXT,
    Amount REAL
);
```

### DebtRegister
```sql
CREATE TABLE DebtRegister (
    DebtName TEXT,
    Amount REAL,
    UnixStamp INTEGER,
    OriginalDebt REAL
);
```

## Features vs Original AutoHotkey Application

### ✅ Implemented Features
- ✅ Invoice viewing and filtering
- ✅ Withdraw management (add, view, delete)
- ✅ CSV upload for withdrawals
- ✅ Quarterly information management
- ✅ Debt tracking and payment recording
- ✅ Debt payment history logs
- ✅ Totals calculation
- ✅ Modern responsive web interface

### 🚧 Features Not Yet Implemented
- ⏳ Excel invoice scanning and generation
- ⏳ Email integration for sending invoices
- ⏳ Advanced Excel data extraction
- ⏳ Batch file processing
- ⏳ File system operations (move to bin)

## Technology Stack

- **Backend:** Flask (Python)
- **Frontend:** Bootstrap 5, Font Awesome
- **Database:** SQLite3
- **Dependencies:** openpyxl for Excel processing

## File Structure

```
FlaskPort/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── templates/            # HTML templates
    ├── base.html         # Base template with navigation
    ├── index.html        # Dashboard
    ├── invoices.html     # Invoice management
    ├── withdraws.html    # Withdraw management
    ├── important_info.html # Quarterly information
    ├── debt.html         # Debt management
    └── debt_log.html     # Debt payment logs
```

## Usage

1. **Dashboard:** Overview of all modules with quick navigation
2. **Invoices:** Filter by year/series, view totals, manage invoice data
3. **Withdraws:** Add manual entries or upload CSV files, track totals
4. **Important Info:** Toggle quarterly payment statuses
5. **Debt:** Add debts, record payments, view payment history

## API Endpoints

- `GET /` - Dashboard
- `GET /invoices` - Invoice listing with filters
- `GET /withdraws` - Withdraw management
- `POST /withdraws/add` - Add manual withdraw
- `POST /withdraws/upload` - Upload CSV withdraws
- `GET /important-info` - Quarterly information
- `POST /important-info/toggle/<kenmerk>` - Toggle payment status
- `GET /debt` - Debt management
- `POST /debt/add` - Add new debt
- `POST /debt/update/<debt_name>` - Record payment
- `GET /debt/log/<debt_name>` - View payment history

## Troubleshooting

### Common Issues

#### "Withdraws or Important Info page not working"

1. **Check database connection:**
   ```cmd
   python test_db.py
   ```

2. **Run the debug script:**
   ```cmd
   python debug.py
   ```

3. **Reinitialize database:**
   ```cmd
   python init_db.py
   ```

#### "Database not found" error

1. Make sure the database path is correct in `config.py`
2. Run `python init_db.py` to create a new database
3. Check that the `data` folder exists in the parent directory

#### "Template not found" error

1. Ensure all files in the `templates/` folder exist
2. Check that Flask can find the templates directory

#### "Module not found" error

1. Install requirements: `pip install -r requirements.txt`
2. Make sure you're in the correct directory

### Debug Tools

- **test_db.py** - Tests database connection
- **debug.py** - Comprehensive system check  
- **init_db.py** - Initializes fresh database (no sample data)
- **clear_database.py** - Clears all existing data from database

## Contributing

This is a direct port of the AutoHotkey application. To add features:

1. Add new routes in `app.py`
2. Create corresponding HTML templates
3. Update the navigation in `base.html`
4. Test with your SQLite database

## License

This port maintains the same structure and functionality as the original AutoHotkey application.
