# Invoice Generator Popup Integration Setup

This document explains how to integrate your existing invoice generator with the Flask app using a popup window approach.

## 🔧 Integration Files Created

1. **`invoice_generator_integration.py`** - Main integration module with Flask routes and database handling
2. **`templates/invoice_generator_popup.html`** - Frontend interface for popup integration
3. **`INVOICE_INTEGRATION_SETUP.md`** - This setup guide

## 📋 Setup Steps

### Step 1: Register the Integration Module

Add this to your main `app.py` file:

```python
# Add this import at the top
from invoice_generator_integration import register_invoice_generator

# Add this line after creating your Flask app
register_invoice_generator(app)
```

### Step 2: Update Navigation

Add a link to the invoice generator in your navigation. Update your `base.html` or navigation template:

```html
<a href="{{ url_for('invoice_generator.create_invoice_popup') }}" class="nav-link">
    <i class="fas fa-file-invoice"></i> Create Invoice
</a>
```

### Step 3: Configure Your Invoice Generator Path

In `templates/invoice_generator_popup.html`, update the `buildGeneratorURL()` function with the correct path to your invoice generator:

```javascript
buildGeneratorURL(config) {
    // Update this line with your actual invoice generator path:
    const baseURL = '/path/to/your/invoice-generator.html';
    
    // Examples:
    // If in static folder: '/static/invoice-generator/index.html'
    // If separate server: 'http://localhost:3000/invoice-generator'
    // If in templates: '/invoice-generator-standalone'
}
```

### Step 4: Modify Your Invoice Generator (Communication)

Add this JavaScript code to your existing invoice generator to communicate with the Flask app:

```javascript
// Add this to your invoice generator's JavaScript

// Function to send completed invoice back to parent window
function sendInvoiceToParent(invoiceData) {
    const message = {
        type: 'invoice_completed',
        invoice: {
            invoice_number: invoiceData.invoice_number,
            client_name: invoiceData.client_name,
            client_email: invoiceData.client_email,
            client_address: invoiceData.client_address,
            date: invoiceData.date, // YYYY-MM-DD format
            due_date: invoiceData.due_date,
            items: invoiceData.items, // Array of line items
            subtotal: invoiceData.subtotal,
            tax_rate: invoiceData.tax_rate,
            tax_amount: invoiceData.tax_amount,
            total: invoiceData.total,
            notes: invoiceData.notes,
            status: 'draft' // or 'sent', 'paid', etc.
        }
    };
    
    // Send to parent window
    if (window.opener && !window.opener.closed) {
        window.opener.postMessage(message, '*');
    }
}

// Function to cancel and close
function cancelInvoice() {
    const message = {
        type: 'invoice_cancelled'
    };
    
    if (window.opener && !window.opener.closed) {
        window.opener.postMessage(message, '*');
    }
    
    window.close();
}

// Notify parent that generator is ready
window.addEventListener('load', () => {
    if (window.opener && !window.opener.closed) {
        window.opener.postMessage({
            type: 'generator_ready'
        }, '*');
    }
});

// Example: Call sendInvoiceToParent when user completes invoice
document.getElementById('your-save-button').addEventListener('click', () => {
    const invoiceData = gatherInvoiceData(); // Your existing function
    sendInvoiceToParent(invoiceData);
    window.close();
});
```

### Step 5: Database Setup

The integration will automatically create the required database tables when first run. The tables created are:

- **`invoices`** - Main invoice records
- **`invoice_items`** - Line items for each invoice

## 🎯 Expected Invoice Data Format

Your invoice generator should send data in this JSON format:

```json
{
    "invoice_number": "INV-001",
    "client_name": "Client Name",
    "client_email": "client@email.com",
    "client_address": "123 Main St, City, State 12345",
    "date": "2025-01-15",
    "due_date": "2025-02-15",
    "items": [
        {
            "description": "Web Development Services",
            "quantity": 10,
            "rate": 75.00,
            "amount": 750.00
        },
        {
            "description": "Hosting Setup",
            "quantity": 1,
            "rate": 100.00,
            "amount": 100.00
        }
    ],
    "subtotal": 850.00,
    "tax_rate": 8.25,
    "tax_amount": 70.13,
    "total": 920.13,
    "notes": "Payment due within 30 days",
    "status": "draft"
}
```

## 🔄 Integration Flow

1. **User clicks "Open Invoice Generator"** in Flask app
2. **Popup window opens** with your invoice generator
3. **User creates invoice** in familiar interface
4. **Invoice data is sent** back to Flask app via JavaScript
5. **Flask app saves** invoice to database
6. **Popup closes** and user sees confirmation
7. **Invoice appears** in the main invoices list

## 🛠 API Endpoints

The integration provides these endpoints:

- **`/invoice-generator/create-invoice-popup`** - Main integration page
- **`/invoice-generator/api/receive-invoice`** - Receives invoice data from popup
- **`/invoice-generator/api/invoice-generator-config`** - Provides config to generator
- **`/invoice-generator/invoices-list`** - Enhanced invoices list

## 🔧 Customization Options

### Invoice Numbering
Modify the `generate_next_invoice_number()` function in `invoice_generator_integration.py` to change numbering format.

### Database Schema
Add additional fields to the invoice tables by modifying the `init_invoice_tables()` function.

### Security
Update the popup message handler to verify the origin of messages for security.

### Styling
Customize the popup integration page by modifying `templates/invoice_generator_popup.html`.

## 🚀 Testing

1. Start your Flask app
2. Navigate to `/invoice-generator/create-invoice-popup`
3. Click "Open Invoice Generator"
4. Complete an invoice in the popup
5. Verify it saves to the database
6. Check the invoices list

## 🐛 Troubleshooting

### Popup Blocked
- Ensure popups are allowed in browser settings
- User must click the button (can't auto-open popups)

### Communication Issues
- Check browser console for JavaScript errors
- Verify the message origin in production
- Ensure your invoice generator calls the communication functions

### Database Errors
- Check that SQLite database is writable
- Verify database path in connection function
- Look at Flask logs for SQL errors

## 🔄 Next Steps (Future Enhancements)

1. **Full Integration** - Embed generator directly in Flask app
2. **PDF Generation** - Add PDF export functionality
3. **Email Integration** - Send invoices directly to clients
4. **Client Management** - Pre-populate client data
5. **Invoice Templates** - Multiple invoice designs
6. **Status Tracking** - Track payment status and history

---

Once you've completed the setup, test the integration and let me know if you need any adjustments or run into issues!
