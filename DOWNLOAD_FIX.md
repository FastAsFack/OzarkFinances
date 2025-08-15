# Invoice Download Fix

## Issue
The invoice download button was failing with the error:
```
ERROR:__main__:Error downloading invoice 250022: 'sqlite3.Row' object has no attribute 'get'
```

## Root Cause
The download function was trying to use the `.get()` method on a `sqlite3.Row` object, which doesn't have this method. This occurred on line 1166 in the `download_invoice` function:

```python
ws['B6'] = invoice.get('payment_status', 'pending')  # ❌ INCORRECT
```

## Solution
Replaced the `.get()` call with proper `sqlite3.Row` access pattern:

```python
# Handle payment_status safely for sqlite3.Row objects
try:
    payment_status = invoice['payment_status'] if 'payment_status' in invoice.keys() else 'pending'
except (KeyError, TypeError):
    payment_status = 'pending'
ws['B6'] = payment_status  # ✅ CORRECT
```

## Additional Improvements
1. **Safe filename generation**: Added protection against backslashes in dates
2. **Error handling**: Enhanced exception handling for column access
3. **Compatibility**: Ensured code works with `sqlite3.Row` objects used throughout the app

## Files Modified
- `app.py`: Fixed the `download_invoice()` function

## Testing
- ✅ Verified `sqlite3.Row` objects don't have `.get()` method
- ✅ Confirmed safe column access works for both existing and missing columns
- ✅ Tested filename generation with various date formats
- ✅ App imports successfully with the fix

## Impact
Users can now successfully download invoices as Excel files without encountering the sqlite3.Row error.
