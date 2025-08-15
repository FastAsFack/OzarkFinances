/**
 * Communication script for Invoice Generator
 * Add this script to your external invoice generator (192.168.1.153:5001)
 * to enable communication back to the main Ozark Finances app
 */

class InvoiceGeneratorBridge {
    constructor() {
        this.parentOrigin = 'http://localhost:5000'; // Main app origin
        this.setupEventListeners();
        this.notifyParentReady();
    }
    
    setupEventListeners() {
        // Listen for messages from parent
        window.addEventListener('message', (event) => {
            if (event.origin !== this.parentOrigin) {
                console.warn('Message from unauthorized origin:', event.origin);
                return;
            }
            
            this.handleParentMessage(event.data);
        });
        
        // Notify parent when page is loaded
        document.addEventListener('DOMContentLoaded', () => {
            this.notifyParentReady();
        });
    }
    
    notifyParentReady() {
        if (window.opener && !window.opener.closed) {
            window.opener.postMessage({
                type: 'generator_ready',
                timestamp: new Date().toISOString()
            }, this.parentOrigin);
            
            console.log('Notified parent that generator is ready');
        }
    }
    
    handleParentMessage(data) {
        console.log('Received message from parent:', data);
        
        switch (data.type) {
            case 'configure':
                this.configureGenerator(data.config);
                break;
            case 'prefill':
                this.prefillForm(data.data);
                break;
            default:
                console.log('Unknown message type from parent:', data.type);
        }
    }
    
    /**
     * Call this method when an invoice is successfully generated
     * Pass the invoice data that should be saved to the main app
     */
    notifyInvoiceCompleted(invoiceData) {
        if (!window.opener || window.opener.closed) {
            console.error('Parent window is not available');
            return;
        }
        
        // Convert your invoice data to the expected format
        const formattedData = this.formatInvoiceData(invoiceData);
        
        window.opener.postMessage({
            type: 'invoice_completed',
            invoice: formattedData,
            timestamp: new Date().toISOString()
        }, this.parentOrigin);
        
        console.log('Sent invoice data to parent:', formattedData);
        
        // Optionally close the popup after a short delay
        setTimeout(() => {
            window.close();
        }, 2000);
    }
    
    /**
     * Call this method if invoice generation is cancelled
     */
    notifyInvoiceCancelled() {
        if (!window.opener || window.opener.closed) {
            console.error('Parent window is not available');
            return;
        }
        
        window.opener.postMessage({
            type: 'invoice_cancelled',
            timestamp: new Date().toISOString()
        }, this.parentOrigin);
        
        console.log('Notified parent that invoice was cancelled');
        window.close();
    }
    
    formatInvoiceData(invoiceData) {
        // Convert your invoice generator's data format to what the main app expects
        // Adjust this based on your invoice generator's actual data structure
        
        return {
            invoice_number: invoiceData.invoice_number || invoiceData.invoiceId || 'INV-000',
            client_name: invoiceData.client_name || invoiceData.clientName || '',
            client_email: invoiceData.client_email || invoiceData.clientEmail || '',
            client_address: invoiceData.client_address || invoiceData.clientAddress || '',
            date: invoiceData.date || invoiceData.invoiceDate || new Date().toISOString().split('T')[0],
            due_date: invoiceData.due_date || invoiceData.dueDate || '',
            subtotal: parseFloat(invoiceData.subtotal || invoiceData.amount || 0),
            tax_rate: parseFloat(invoiceData.tax_rate || invoiceData.taxRate || 0),
            tax_amount: parseFloat(invoiceData.tax_amount || invoiceData.taxAmount || 0),
            total: parseFloat(invoiceData.total || invoiceData.totalAmount || 0),
            notes: invoiceData.notes || invoiceData.description || '',
            status: invoiceData.status || 'completed',
            items: invoiceData.items || []
        };
    }
    
    configureGenerator(config) {
        // Handle configuration from parent
        console.log('Configuring generator with:', config);
    }
    
    prefillForm(data) {
        // Handle form prefilling from parent
        console.log('Prefilling form with:', data);
    }
}

// Initialize the bridge when script loads
const invoiceBridge = new InvoiceGeneratorBridge();

// Make it globally available for your invoice generator to use
window.InvoiceBridge = invoiceBridge;

// Example usage in your invoice generator:
/*
// When invoice is completed, call:
window.InvoiceBridge.notifyInvoiceCompleted({
    invoice_number: 'NEW001',
    client_name: 'Client Name',
    date: '2025-07-23',
    subtotal: 100.00,
    tax_amount: 21.00,
    total: 121.00
});

// When invoice is cancelled, call:
window.InvoiceBridge.notifyInvoiceCancelled();
*/
