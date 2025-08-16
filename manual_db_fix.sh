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
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS Withdraw (Date TEXT NOT NULL, Amount REAL NOT NULL);"

echo "Creating KwartaalData table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS KwartaalData (tijdvak TEXT NOT NULL, betaling TEXT NOT NULL, kenmerk TEXT PRIMARY KEY, betaald TEXT NOT NULL, Amount REAL NOT NULL);"

echo "Creating DebtRegister table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS DebtRegister (DebtName TEXT PRIMARY KEY, Amount REAL NOT NULL, UnixStamp INTEGER NOT NULL, OriginalDebt REAL NOT NULL);"

echo "Verifying tables..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db ".tables"

echo "Checking database file..."
docker compose exec ozark-finances ls -la /app/data/

echo "✅ Manual database fix completed!"
echo "🔄 Please restart the container to pick up the changes:"
echo "docker compose restart ozark-finances"
