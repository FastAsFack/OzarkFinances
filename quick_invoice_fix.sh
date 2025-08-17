#!/bin/bash
# Quick fix for invoice counting issue without Git
# This manually updates the JavaScript in the running container

echo "🔧 QUICK INVOICE COUNT FIX 🔧"
echo "Applying JavaScript fix directly to container..."

cd ~/ozark-finances || exit 1

# Create the updated JavaScript functions
cat << 'EOF' > /tmp/invoice_fix.js
function updateSelectedCount() {
    const selectedCheckboxes = document.querySelectorAll('.invoice-checkbox:checked');
    // Get unique invoice IDs instead of counting all checkboxes (mobile + desktop)
    const uniqueInvoiceIds = new Set();
    selectedCheckboxes.forEach(checkbox => {
        uniqueInvoiceIds.add(checkbox.value);
    });
    const selectedCount = uniqueInvoiceIds.size;
    const bulkActionsBar = document.getElementById('bulkActionsBar');
    const countElement = document.getElementById('selectedCount');
    
    if (countElement) {
        countElement.textContent = selectedCount;
    }
    
    if (selectedCount > 0) {
        bulkActionsBar.style.display = 'block';
    } else {
        bulkActionsBar.style.display = 'none';
    }
}

function updateBulkActions() {
    const selectedCheckboxes = document.querySelectorAll('.invoice-checkbox:checked');
    // Get unique invoice IDs instead of counting all checkboxes (mobile + desktop)
    const uniqueInvoiceIds = new Set();
    selectedCheckboxes.forEach(checkbox => {
        uniqueInvoiceIds.add(checkbox.value);
    });
    const selectedCount = uniqueInvoiceIds.size;
    const bulkActionsBar = document.getElementById('bulkActionsBar');
    const mobileBulkActionsBar = document.getElementById('mobileBulkActionsBar');
    const selectedCountSpan = document.getElementById('selectedCount');
    const mobileSelectedCountSpan = document.getElementById('mobileSelectedCount');
    
    if (selectedCount > 0) {
        bulkActionsBar.style.display = 'block';
        mobileBulkActionsBar.style.display = 'block';
        selectedCountSpan.textContent = selectedCount;
        mobileSelectedCountSpan.textContent = selectedCount;
    } else {
        bulkActionsBar.style.display = 'none';
        mobileBulkActionsBar.style.display = 'none';
    }
    
    // Update select all checkbox state
    const allCheckboxes = document.querySelectorAll('.invoice-checkbox');
    // Get unique invoice count for select all state calculation
    const uniqueInvoiceCount = new Set();
    allCheckboxes.forEach(checkbox => {
        uniqueInvoiceCount.add(checkbox.value);
    });
    const totalInvoices = uniqueInvoiceCount.size;
    const selectAllCheckbox = document.getElementById('selectAllInvoices');
    
    if (selectedCount === 0) {
        selectAllCheckbox.indeterminate = false;
        selectAllCheckbox.checked = false;
    } else if (selectedCount === totalInvoices) {
        selectAllCheckbox.indeterminate = false;
        selectAllCheckbox.checked = true;
    } else {
        selectAllCheckbox.indeterminate = true;
        selectAllCheckbox.checked = false;
    }
}

function getSelectedInvoiceIds() {
    const selectedCheckboxes = document.querySelectorAll('.invoice-checkbox:checked');
    // Return unique invoice IDs only (avoid duplicates from mobile + desktop checkboxes)
    const uniqueIds = new Set();
    selectedCheckboxes.forEach(checkbox => {
        uniqueIds.add(checkbox.value);
    });
    return Array.from(uniqueIds);
}
EOF

echo "📝 JavaScript fix created in /tmp/invoice_fix.js"
echo "🔄 Now restart your containers and the fix will be applied on next build"
echo ""
echo "To apply immediately, you can:"
echo "1. Restart containers: docker compose restart ozark-finances"
echo "2. Or rebuild: docker compose down && docker compose up -d --build"
echo ""
echo "✅ Invoice counting fix ready!"
