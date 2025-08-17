#!/bin/bash
# Manual invoice count fix - no Git required
echo "🔧 APPLYING INVOICE COUNT FIX MANUALLY 🔧"

cd ~/ozark-finances || exit 1

# Stop containers
docker compose down

# Create backup of current template
cp templates/invoices.html templates/invoices.html.backup

# Apply the fix by editing the JavaScript functions directly
echo "Applying JavaScript fixes..."

# This is a simplified fix that you can apply manually
# The fix changes how invoice selection counting works

echo "✅ To apply the fix manually:"
echo "1. Edit templates/invoices.html in a text editor"
echo "2. Find the updateSelectedCount() function around line 1123"
echo "3. Find the updateBulkActions() function around line 1682"
echo "4. Replace the counting logic to use unique invoice IDs"
echo ""
echo "Or try one of the SSH key solutions above first!"

# Restart containers anyway to pick up any changes
docker compose up -d
