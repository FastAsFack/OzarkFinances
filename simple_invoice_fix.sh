#!/bin/bash
# Simple offline invoice count fix
# Just copy-paste this entire script to your Pi terminal

echo "🔧 OFFLINE INVOICE COUNT FIX 🔧"
cd ~/ozark-finances || exit 1

# Create a simple JavaScript patch file
cat > /tmp/invoice_patch.js << 'JSEOF'
// Patched JavaScript functions to fix invoice counting
// This replaces the problematic functions in the invoices.html template

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
JSEOF

echo "📝 JavaScript patch created in /tmp/invoice_patch.js"
echo ""
echo "Now manually replace the JavaScript functions in templates/invoices.html"
echo "Or just restart containers and it should pick up the latest code:"
echo ""
echo "docker compose down"
echo "docker compose up -d --build"
echo ""
echo "✅ Ready to apply fix!"
