#!/bin/bash
# Comprehensive database debug and fix script
# This will diagnose and fix the database issue step by step

echo "🔍 COMPREHENSIVE DATABASE DIAGNOSIS AND FIX 🔍"
echo "================================================"

# Check if we're in the right directory
echo "1. Current directory: $(pwd)"
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Not in the right directory! Looking for ozark-finances..."
    cd ~/ozark-finances 2>/dev/null || cd /home/ozark/ozark-finances 2>/dev/null || exit 1
    echo "✅ Changed to: $(pwd)"
fi

# Check Docker Compose status
echo ""
echo "2. Docker Compose Status:"
docker compose ps

# Check if container is running
echo ""
echo "3. Container Status:"
CONTAINER_RUNNING=$(docker compose ps | grep ozark-finances | grep "Up" | wc -l)
if [ "$CONTAINER_RUNNING" -eq "0" ]; then
    echo "❌ Container is not running! Starting it..."
    docker compose up -d
    sleep 5
else
    echo "✅ Container is running"
fi

# Check mounted volumes
echo ""
echo "4. Checking mounted volumes in container:"
docker compose exec ozark-finances df -h | grep "/app"
docker compose exec ozark-finances ls -la /app/

# Check data directory
echo ""
echo "5. Checking /app/data directory:"
docker compose exec ozark-finances ls -la /app/data/ 2>/dev/null || echo "❌ /app/data does not exist"

# Create data directory if it doesn't exist
echo ""
echo "6. Creating data directory:"
docker compose exec ozark-finances mkdir -p /app/data
docker compose exec ozark-finances ls -la /app/data/

# Check if SQLite is available in container
echo ""
echo "7. Testing SQLite availability:"
docker compose exec ozark-finances which sqlite3
docker compose exec ozark-finances sqlite3 --version

# Check current database file
echo ""
echo "8. Checking current database file:"
docker compose exec ozark-finances ls -la /app/data/ozark_finances.db 2>/dev/null || echo "❌ Database file does not exist"

# Create database file and tables - FORCE IT
echo ""
echo "9. FORCE CREATING DATABASE AND TABLES:"

echo "Creating Invoices table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS Invoices (InvoiceID TEXT PRIMARY KEY, InvoiceDate TEXT NOT NULL, Excl REAL NOT NULL, BTW REAL NOT NULL, Incl REAL NOT NULL, status TEXT DEFAULT 'active', deleted_at TEXT NULL, payment_status TEXT DEFAULT 'pending');"
echo "Exit code: $?"

echo "Creating Withdraw table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS Withdraw (Date TEXT NOT NULL, Amount REAL NOT NULL);"
echo "Exit code: $?"

echo "Creating KwartaalData table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS KwartaalData (tijdvak TEXT NOT NULL, betaling TEXT NOT NULL, kenmerk TEXT PRIMARY KEY, betaald TEXT NOT NULL, Amount REAL NOT NULL);"
echo "Exit code: $?"

echo "Creating DebtRegister table..."
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS DebtRegister (DebtName TEXT PRIMARY KEY, Amount REAL NOT NULL, UnixStamp INTEGER NOT NULL, OriginalDebt REAL NOT NULL);"
echo "Exit code: $?"

# Verify database file was created
echo ""
echo "10. Verifying database file after creation:"
docker compose exec ozark-finances ls -la /app/data/ozark_finances.db
docker compose exec ozark-finances file /app/data/ozark_finances.db

# Check tables in database
echo ""
echo "11. Checking tables in database:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db ".tables"

# Check table schema
echo ""
echo "12. Checking Invoices table schema:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db ".schema Invoices"

# Test database access from Python
echo ""
echo "13. Testing database access from Python in container:"
docker compose exec ozark-finances python -c "
import sqlite3
import os
db_path = '/app/data/ozark_finances.db'
print(f'Database path: {db_path}')
print(f'File exists: {os.path.exists(db_path)}')
if os.path.exists(db_path):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
        tables = cursor.fetchall()
        print(f'Tables found: {[t[0] for t in tables]}')
        cursor.execute('SELECT COUNT(*) FROM Invoices')
        count = cursor.fetchone()[0]
        print(f'Invoices table has {count} records')
        conn.close()
        print('✅ Database access successful!')
    except Exception as e:
        print(f'❌ Database access failed: {e}')
else:
    print('❌ Database file does not exist')
"

# Check environment variables
echo ""
echo "14. Checking environment variables in container:"
docker compose exec ozark-finances env | grep -E "(DATABASE_PATH|DATA_DIR)"

# Restart the application to pick up changes
echo ""
echo "15. Restarting application to pick up changes:"
docker compose restart ozark-finances

echo ""
echo "🎉 DIAGNOSIS AND FIX COMPLETED!"
echo "Now test your application - the database should be working!"
