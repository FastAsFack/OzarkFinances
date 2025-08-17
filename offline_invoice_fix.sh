#!/bin/bash
# Invoice count fix script - no internet required
# Copy and paste this entire script to your Pi

echo "🔧 APPLYING INVOICE COUNT FIX (OFFLINE) 🔧"
echo "Fixing the duplicate counting issue..."

cd ~/ozark-finances || exit 1

# Create backup of current template
cp templates/invoices.html templates/invoices.html.backup

# Apply the JavaScript fix using sed commands
echo "📝 Patching JavaScript functions..."

# Fix updateSelectedCount function
sed -i '/function updateSelectedCount() {/,/^}$/ {
    /const selectedCount = selectedCheckboxes.length;/c\
    // Get unique invoice IDs instead of counting all checkboxes (mobile + desktop)\
    const uniqueInvoiceIds = new Set();\
    selectedCheckboxes.forEach(checkbox => {\
        uniqueInvoiceIds.add(checkbox.value);\
    });\
    const selectedCount = uniqueInvoiceIds.size;
}' templates/invoices.html

# Fix updateBulkActions function
sed -i '/function updateBulkActions() {/,/} else if (selectedCount === allCheckboxes.length) {/ {
    /const selectedCount = selectedCheckboxes.length;/c\
    // Get unique invoice IDs instead of counting all checkboxes (mobile + desktop)\
    const uniqueInvoiceIds = new Set();\
    selectedCheckboxes.forEach(checkbox => {\
        uniqueInvoiceIds.add(checkbox.value);\
    });\
    const selectedCount = uniqueInvoiceIds.size;
    
    /} else if (selectedCount === allCheckboxes.length) {/i\
    // Get unique invoice count for select all state calculation\
    const uniqueInvoiceCount = new Set();\
    allCheckboxes.forEach(checkbox => {\
        uniqueInvoiceCount.add(checkbox.value);\
    });\
    const totalInvoices = uniqueInvoiceCount.size;\
    \
    if (selectedCount === 0) {\
        selectAllCheckbox.indeterminate = false;\
        selectAllCheckbox.checked = false;\
    } else if (selectedCount === totalInvoices) {
    
    /} else if (selectedCount === allCheckboxes.length) {/d
}' templates/invoices.html

# Fix getSelectedInvoiceIds function
sed -i '/function getSelectedInvoiceIds() {/,/^}$/ {
    /return Array.from(selectedCheckboxes).map(checkbox => checkbox.value);/c\
    // Return unique invoice IDs only (avoid duplicates from mobile + desktop checkboxes)\
    const uniqueIds = new Set();\
    selectedCheckboxes.forEach(checkbox => {\
        uniqueIds.add(checkbox.value);\
    });\
    return Array.from(uniqueIds);
}' templates/invoices.html

echo "🔄 Rebuilding containers with fix..."
docker compose down
docker compose up -d --build

echo "✅ Invoice count fix applied!"
echo "📊 Now when you select all items, it should show 22 instead of 44"
echo ""
echo "🔙 If something goes wrong, restore backup with:"
echo "cp templates/invoices.html.backup templates/invoices.html"
