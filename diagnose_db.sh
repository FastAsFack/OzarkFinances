#!/bin/bash
# Database diagnostic and permission fix script
# Run this on the Pi to diagnose database issues

echo "🔍 DATABASE DIAGNOSTIC & FIX 🔍"
echo "Checking database permissions and functionality..."

cd ~/ozark-finances || exit 1

echo "1. Checking database file permissions:"
docker compose exec ozark-finances ls -la /app/data/ozark_finances.db

echo ""
echo "2. Checking database file ownership:"
docker compose exec ozark-finances stat /app/data/ozark_finances.db

echo ""
echo "3. Testing database write permissions:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "CREATE TABLE IF NOT EXISTS test_write (id INTEGER); DROP TABLE test_write;"
echo "Write test result: $?"

echo ""
echo "4. Checking all existing tables:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db ".tables"

echo ""
echo "5. Checking Invoices table schema:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db ".schema Invoices"

echo ""
echo "6. Testing insert into Invoices table:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "INSERT OR IGNORE INTO Invoices (InvoiceID, InvoiceDate, Excl, BTW, Incl) VALUES ('TEST001', '2025-08-16', 100.0, 21.0, 121.0);"
echo "Insert test result: $?"

echo ""
echo "7. Checking if test record was inserted:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "SELECT COUNT(*) FROM Invoices WHERE InvoiceID='TEST001';"

echo ""
echo "8. Cleaning up test record:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "DELETE FROM Invoices WHERE InvoiceID='TEST001';"

echo ""
echo "9. Checking application container logs for errors:"
docker compose logs ozark-finances --tail=20

echo ""
echo "10. Fixing database permissions:"
docker compose exec ozark-finances chown -R app:app /app/data/
docker compose exec ozark-finances chmod 664 /app/data/ozark_finances.db
docker compose exec ozark-finances chmod 755 /app/data/

echo ""
echo "11. Restarting application to pick up changes:"
docker compose restart ozark-finances

echo ""
echo "✅ Database diagnostic complete!"
echo "🌐 Try adding an invoice now - it should work!"
echo ""
echo "If it still doesn't work, check the container logs:"
echo "docker compose logs ozark-finances -f"
