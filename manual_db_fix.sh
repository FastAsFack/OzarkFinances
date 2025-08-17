#!/bin/bash
# Manual database initialization script
# Run this on the Pi to fix the database immediately

echo "🚨 EMERGENCY DATABASE FIX 🚨"
echo "Creating database tables manually..."

# Navigate to the deployment directory
cd ~/ozark-finances || exit 1

# Create tables directly using docker exec (using correct service name: ozark-finances)
echo "Creating Invoices table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS Invoices (InvoiceID TEXT PRIMARY KEY, InvoiceDate TEXT NOT NULL, Excl REAL NOT NULL, BTW REAL NOT NULL, Incl REAL NOT NULL, status TEXT DEFAULT 'active', deleted_at TEXT NULL, payment_status TEXT DEFAULT 'pending');"

echo "Creating Withdraw table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS Withdraw (id INTEGER PRIMARY KEY AUTOINCREMENT, Date TEXT NOT NULL, Amount REAL NOT NULL, Description TEXT DEFAULT '');"

echo "Adding ID column to existing Withdraw table (if missing)..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "ALTER TABLE Withdraw ADD COLUMN id INTEGER PRIMARY KEY AUTOINCREMENT;" 2>/dev/null || echo "ID column already exists or table structure is correct"

echo "Adding Description column to existing Withdraw table (if missing)..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "ALTER TABLE Withdraw ADD COLUMN Description TEXT DEFAULT '';" 2>/dev/null || echo "Description column already exists or table structure is correct"

echo "Creating KwartaalData table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS KwartaalData (tijdvak TEXT NOT NULL, betaling TEXT NOT NULL, kenmerk TEXT PRIMARY KEY, betaald TEXT NOT NULL, Amount REAL NOT NULL);"

echo "Creating DebtRegister table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS DebtRegister (DebtName TEXT PRIMARY KEY, Amount REAL NOT NULL, UnixStamp INTEGER NOT NULL, OriginalDebt REAL NOT NULL, Category TEXT DEFAULT 'General', DueDate TEXT DEFAULT '', MinimumPayment REAL DEFAULT 0, InterestRate REAL DEFAULT 0, Notes TEXT DEFAULT '', AddedDate TEXT DEFAULT '');"

echo "Creating btw_quarterly_payments table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS btw_quarterly_payments (id INTEGER PRIMARY KEY AUTOINCREMENT, timeframe TEXT NOT NULL, quarter_months TEXT NOT NULL, latest_payment_date TEXT NOT NULL, payment_id TEXT, cost REAL NOT NULL, actual_payment_date TEXT, status TEXT DEFAULT 'pending', notes TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP, UNIQUE(timeframe));"

echo "Creating btw_quarterly_payments indexes..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE INDEX IF NOT EXISTS idx_btw_timeframe ON btw_quarterly_payments(timeframe);"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE INDEX IF NOT EXISTS idx_btw_status ON btw_quarterly_payments(status);"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE INDEX IF NOT EXISTS idx_btw_payment_date ON btw_quarterly_payments(latest_payment_date);"

echo "Adding Category column to existing DebtRegister table (if missing)..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "ALTER TABLE DebtRegister ADD COLUMN Category TEXT DEFAULT 'General';" 2>/dev/null || echo "Category column already exists or table structure is correct"

echo "Adding DueDate column to existing DebtRegister table (if missing)..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "ALTER TABLE DebtRegister ADD COLUMN DueDate TEXT DEFAULT '';" 2>/dev/null || echo "DueDate column already exists or table structure is correct"

echo "Adding MinimumPayment column to existing DebtRegister table (if missing)..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "ALTER TABLE DebtRegister ADD COLUMN MinimumPayment REAL DEFAULT 0;" 2>/dev/null || echo "MinimumPayment column already exists or table structure is correct"

echo "Adding InterestRate column to existing DebtRegister table (if missing)..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "ALTER TABLE DebtRegister ADD COLUMN InterestRate REAL DEFAULT 0;" 2>/dev/null || echo "InterestRate column already exists or table structure is correct"

echo "Adding Notes column to existing DebtRegister table (if missing)..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "ALTER TABLE DebtRegister ADD COLUMN Notes TEXT DEFAULT '';" 2>/dev/null || echo "Notes column already exists or table structure is correct"

echo "Adding AddedDate column to existing DebtRegister table (if missing)..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "ALTER TABLE DebtRegister ADD COLUMN AddedDate TEXT DEFAULT '';" 2>/dev/null || echo "AddedDate column already exists or table structure is correct"

echo "Populating default quarterly BTW payments for 2025..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "INSERT OR IGNORE INTO btw_quarterly_payments (timeframe, quarter_months, latest_payment_date, cost, status) VALUES ('Q1 2025', 'Jan-Mar', '2025-04-30', 0.0, 'pending');"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "INSERT OR IGNORE INTO btw_quarterly_payments (timeframe, quarter_months, latest_payment_date, cost, status) VALUES ('Q2 2025', 'Apr-Jun', '2025-07-31', 0.0, 'pending');"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "INSERT OR IGNORE INTO btw_quarterly_payments (timeframe, quarter_months, latest_payment_date, cost, status) VALUES ('Q3 2025', 'Jul-Sep', '2025-10-31', 0.0, 'pending');"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "INSERT OR IGNORE INTO btw_quarterly_payments (timeframe, quarter_months, latest_payment_date, cost, status) VALUES ('Q4 2025', 'Oct-Dec', '2026-01-31', 0.0, 'pending');"

echo "Verifying quarterly payments were added..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "SELECT timeframe, quarter_months, latest_payment_date, status FROM btw_quarterly_payments ORDER BY timeframe;"

echo "Checking for existing debt data to migrate..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "SELECT COUNT(*) as debt_count FROM DebtRegister;"

echo "Final debt count check..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "SELECT COUNT(*) as total_debts FROM DebtRegister;"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE INDEX IF NOT EXISTS idx_btw_payment_date ON btw_quarterly_payments(latest_payment_date);"

echo "Verifying tables..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db ".tables"

echo "Checking database file..."
docker compose exec ozark-finances ls -la /app/data/

echo "✅ Manual database fix completed!"
echo "🔄 Please restart the container to pick up the changes:"
echo "docker compose restart ozark-finances"
