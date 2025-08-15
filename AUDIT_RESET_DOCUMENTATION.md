# 🛠️ AUDIT LOGS RESET UTILITY

## 📋 Overview

The **Audit Logs Reset Script** provides a safe and comprehensive way to clear all audit logs from the Ozark Finances audit tracking system. This utility is useful for testing, maintenance, or starting fresh with audit tracking.

## 📁 Files Created

### **Main Script**
- `reset_audit_logs.py` - Python script with full functionality
- `reset_audit_logs.bat` - Windows batch file for easy execution

## 🚀 Usage Options

### **1. Show Statistics Only**
```bash
python reset_audit_logs.py --stats
```
**Purpose:** View current audit log statistics without making changes
**Output:** 
- Total record count
- Action breakdown (INSERT, UPDATE, DELETE, etc.)
- Table breakdown (Invoices, Withdraws, etc.)
- Date range of logs
- Database file size

### **2. Interactive Reset (with confirmation)**
```bash
python reset_audit_logs.py
```
**Purpose:** Reset audit logs with safety confirmation prompt
**Process:**
- Shows current statistics
- Asks for confirmation before proceeding
- Creates backup if requested
- Clears all audit logs
- Optimizes database

### **3. Force Reset (no confirmation)**
```bash
python reset_audit_logs.py --force
```
**Purpose:** Reset without confirmation prompt (for scripts/automation)
**⚠️ Warning:** Use with caution - no confirmation asked!

### **4. Reset with Backup**
```bash
python reset_audit_logs.py --backup
```
**Purpose:** Create timestamped backup before clearing logs
**Backup Format:** `audit_tracker_backup_YYYYMMDD_HHMMSS.db`

### **5. Custom Database Path**
```bash
python reset_audit_logs.py --db /path/to/audit_tracker.db
```
**Purpose:** Specify custom database location

### **6. Combined Options**
```bash
python reset_audit_logs.py --backup --force --db custom_audit.db
```

## 🎯 What Gets Reset

### **Cleared Data**
✅ **All audit log entries** - Complete log history  
✅ **Auto-increment counters** - Next ID starts from 1  
✅ **Database optimization** - VACUUM reclaims space  

### **Preserved Data**
✅ **Database schema** - Table structure intact  
✅ **Audit tracking functionality** - System continues working  
✅ **Main application data** - Invoices/withdraws/debts unchanged  

## 🔒 Safety Features

### **Confirmation System**
- Interactive confirmation prompt by default
- Shows current statistics before reset
- Clear warning about permanent deletion
- Option to cancel operation

### **Backup Support**
- Optional automatic backup creation
- Timestamped backup files
- Full database copy preservation
- Backup verification

### **Error Handling**
- Database existence validation
- Connection error handling
- Operation verification
- Graceful failure handling

## 📊 Example Output

### **Statistics View**
```
📊 AUDIT LOG STATISTICS
==============================
Total Records: 1,250
Date Range: 2025-01-01 10:00:00 to 2025-07-26 16:55:26

📝 Actions Breakdown:
   INSERT: 450
   UPDATE: 380
   DELETE: 120
   SELECT: 200
   TRANSACTION_START: 50
   TRANSACTION_COMPLETE: 50

📋 Tables Breakdown:
   Invoices: 600
   Withdraw: 400
   DebtRegister: 200
   SYSTEM: 50

💾 Database Size: 2.45 MB
```

### **Reset Process**
```
🔄 AUDIT LOGS RESET UTILITY
==================================================
📍 Database: audit_tracker.db
📊 Current audit logs: 1,250
📅 Date range: 2025-01-01 to 2025-07-26

⚠️  WARNING: This will permanently delete ALL audit logs!
   This action cannot be undone.

🤔 Are you sure you want to clear all audit logs? (yes/no): yes

💾 Backup created: audit_tracker_backup_20250726_165530.db

🔄 Clearing 1,250 audit log entries...
✅ Audit logs cleared successfully!
📊 Database reset and optimized
✅ Verification: Database is now empty (0 records)

🎉 Audit logs reset completed successfully!
```

## 🔧 Technical Details

### **Database Operations**
1. **Count Verification** - Check current log count
2. **Backup Creation** - Optional timestamped backup
3. **Data Deletion** - `DELETE FROM audit_log`
4. **Counter Reset** - Reset auto-increment sequence
5. **Optimization** - `VACUUM` to reclaim space
6. **Verification** - Confirm empty database

### **File Management**
- Automatic database path resolution
- Backup file naming with timestamps
- File size reporting and optimization
- Cross-platform compatibility

## ⚠️ Important Notes

### **Before Running**
1. **Stop audit viewer** if currently running
2. **Consider creating backup** for important audit history
3. **Notify team members** if in shared environment
4. **Verify database path** if using custom location

### **After Running**
1. **Restart audit viewer** to refresh display
2. **New audit logs** will start from ID 1
3. **Main application** continues normal operation
4. **Audit tracking** resumes immediately

## 🎯 Use Cases

### **Development & Testing**
- Clear test data between development cycles
- Reset for clean testing environment
- Remove development audit clutter

### **Maintenance**
- Regular cleanup of old audit logs
- Database optimization and cleanup
- Disk space management

### **Troubleshooting**
- Clear corrupted audit data
- Reset after audit system issues
- Start fresh after major changes

## 🛡️ Security Considerations

### **Data Protection**
- Audit logs contain sensitive operation history
- Backup recommended before clearing
- Consider data retention policies
- Document reset operations

### **Access Control**
- Restrict script access to authorized users
- Monitor reset operations
- Log reset activities in main system
- Maintain reset operation records

## 🚀 Quick Start

### **Windows Users**
1. Double-click `reset_audit_logs.bat`
2. Follow interactive prompts
3. Confirm when ready to proceed

### **Command Line Users**
```bash
# View current statistics
python reset_audit_logs.py --stats

# Reset with backup and confirmation
python reset_audit_logs.py --backup

# Force reset (no confirmation)
python reset_audit_logs.py --force
```

## ✅ Verification

After running the reset, verify success by:
1. **Check script output** for success messages
2. **View statistics** with `--stats` option
3. **Access audit viewer** at http://localhost:5001
4. **Confirm empty dashboard** and log views
5. **Test new audit tracking** by making changes in main app

---

**🎉 The audit logs reset utility provides safe, comprehensive audit log management for the Ozark Finances system!**
