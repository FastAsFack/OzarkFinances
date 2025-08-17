#!/bin/bash
# Fix missing Category column in DebtRegister table
# Run this on the Pi to fix the debt page

echo "🔧 FIXING DEBT PAGE - ADDING CATEGORY COLUMN 🔧"
cd ~/ozark-finances || exit 1

echo "1. Checking current DebtRegister table schema:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db ".schema DebtRegister"

echo ""
echo "2. Adding missing Category column to DebtRegister table:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "ALTER TABLE DebtRegister ADD COLUMN Category TEXT DEFAULT 'General';"
echo "Add column result: $?"

echo ""
echo "3. Verifying updated schema:"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db ".schema DebtRegister"

echo ""
echo "4. Testing debt data (if any exists):"
docker compose exec ozark-finances sqlite3 /app/data/ozark_finances.db "SELECT COUNT(*) as debt_count FROM DebtRegister;"

echo ""
echo "5. Restarting application:"
docker compose restart ozark-finances

echo ""
echo "✅ Debt page fix complete!"
echo "🌐 The debt page should now work without errors!"
echo ""
echo "Now try:"
echo "1. Adding a new invoice - should work"
echo "2. Visiting the debt page - should work" 
echo "3. Adding debt entries - should work"
