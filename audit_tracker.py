"""
Audit Tracker for Ozark Finances
Tracks all database changes with timestamp precision and field-level tracking
"""

import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

class AuditTracker:
    def __init__(self, audit_db_path='audit_tracker.db'):
        self.audit_db_path = audit_db_path
        self.init_audit_database()
    
    def init_audit_database(self):
        """Initialize the audit database with optimized structure"""
        with sqlite3.connect(self.audit_db_path) as conn:
            cursor = conn.cursor()
            
            # Main audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    action TEXT NOT NULL,
                    table_name TEXT NOT NULL,
                    record_id TEXT NOT NULL,
                    user_info TEXT,
                    changes TEXT,
                    old_values TEXT,
                    new_values TEXT,
                    ip_address TEXT,
                    user_agent TEXT,
                    session_id TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                ON audit_log(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_table_action 
                ON audit_log(table_name, action)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_record_id 
                ON audit_log(record_id)
            """)
            
            # Statistics view for dashboard
            cursor.execute("""
                CREATE VIEW IF NOT EXISTS audit_statistics AS
                SELECT 
                    table_name,
                    action,
                    COUNT(*) as count,
                    MAX(timestamp) as last_activity,
                    MIN(timestamp) as first_activity
                FROM audit_log
                GROUP BY table_name, action
            """)
            
            conn.commit()
            logger.info("Audit database initialized successfully")
    
    def log_action(self, action, table_name, record_id, old_values=None, new_values=None, 
                   user_info=None, request=None):
        """
        Log an action to the audit trail
        
        Args:
            action: INSERT, UPDATE, DELETE, SELECT
            table_name: Name of the table affected
            record_id: ID of the record affected
            old_values: Previous values (for UPDATE/DELETE)
            new_values: New values (for INSERT/UPDATE)
            user_info: User information
            request: Flask request object for IP/user agent
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            
            # Calculate changes for UPDATE operations
            changes = {}
            if action == 'UPDATE' and old_values and new_values:
                changes = self._calculate_changes(old_values, new_values)
            
            # Extract request information
            ip_address = None
            user_agent = None
            session_id = None
            
            if request:
                ip_address = request.remote_addr
                user_agent = request.headers.get('User-Agent', '')
                session_id = str(request.session.get('session_id', ''))
            
            with sqlite3.connect(self.audit_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO audit_log 
                    (timestamp, action, table_name, record_id, user_info, changes, 
                     old_values, new_values, ip_address, user_agent, session_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    timestamp,
                    action,
                    table_name,
                    str(record_id),
                    json.dumps(user_info) if user_info else None,
                    json.dumps(changes) if changes else None,
                    json.dumps(old_values) if old_values else None,
                    json.dumps(new_values) if new_values else None,
                    ip_address,
                    user_agent,
                    session_id
                ))
                conn.commit()
                
            logger.info(f"Audit logged: {action} on {table_name}#{record_id}")
            
        except Exception as e:
            logger.error(f"Failed to log audit action: {e}")
    
    def _calculate_changes(self, old_values, new_values):
        """Calculate field-level changes between old and new values"""
        changes = {}
        
        # Convert to dicts if they're sqlite Row objects
        if hasattr(old_values, 'keys'):
            old_dict = dict(old_values)
        else:
            old_dict = old_values
            
        if hasattr(new_values, 'keys'):
            new_dict = dict(new_values)
        else:
            new_dict = new_values
        
        # Find all unique keys
        all_keys = set(old_dict.keys()) | set(new_dict.keys())
        
        for key in all_keys:
            old_val = old_dict.get(key)
            new_val = new_dict.get(key)
            
            if old_val != new_val:
                changes[key] = {
                    'old': old_val,
                    'new': new_val
                }
        
        return changes
    
    def get_audit_logs(self, table_name=None, action=None, record_id=None, 
                       date_from=None, date_to=None, limit=100, offset=0):
        """Retrieve audit logs with filtering"""
        query = "SELECT * FROM audit_log WHERE 1=1"
        params = []
        
        if table_name:
            query += " AND table_name = ?"
            params.append(table_name)
        
        if action:
            query += " AND action = ?"
            params.append(action)
        
        if record_id:
            query += " AND record_id = ?"
            params.append(str(record_id))
        
        if date_from:
            query += " AND timestamp >= ?"
            params.append(date_from)
        
        if date_to:
            query += " AND timestamp <= ?"
            params.append(date_to)
        
        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with sqlite3.connect(self.audit_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def get_statistics(self):
        """Get audit statistics for dashboard"""
        with sqlite3.connect(self.audit_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Overall statistics
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_actions,
                    COUNT(DISTINCT table_name) as tables_tracked,
                    COUNT(DISTINCT record_id) as records_affected,
                    MAX(timestamp) as last_activity,
                    MIN(timestamp) as first_activity
                FROM audit_log
            """)
            overall_stats = cursor.fetchone()
            
            # Action breakdown
            cursor.execute("""
                SELECT action, COUNT(*) as count
                FROM audit_log
                GROUP BY action
                ORDER BY count DESC
            """)
            action_stats = cursor.fetchall()
            
            # Table activity
            cursor.execute("""
                SELECT table_name, COUNT(*) as count, MAX(timestamp) as last_activity
                FROM audit_log
                GROUP BY table_name
                ORDER BY count DESC
            """)
            table_stats = cursor.fetchall()
            
            # Recent activity (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM audit_log
                WHERE timestamp >= datetime('now', '-1 day')
            """)
            recent_activity = cursor.fetchone()
            
            return {
                'overall': dict(overall_stats) if overall_stats else {},
                'actions': [dict(row) for row in action_stats],
                'tables': [dict(row) for row in table_stats],
                'recent_activity': dict(recent_activity) if recent_activity else {}
            }
    
    def get_record_history(self, table_name, record_id):
        """Get complete history for a specific record"""
        return self.get_audit_logs(table_name=table_name, record_id=record_id, limit=1000)

# Global audit tracker instance
audit_tracker = AuditTracker()

# Decorator for automatic audit logging
def audit_log(action, table_name, get_record_id=None):
    """
    Decorator to automatically log database operations
    
    Args:
        action: Action type (INSERT, UPDATE, DELETE)
        table_name: Table name
        get_record_id: Function to extract record ID from function args
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                # Execute the original function
                result = func(*args, **kwargs)
                
                # Extract record ID
                record_id = None
                if get_record_id:
                    record_id = get_record_id(*args, **kwargs)
                elif args:
                    record_id = args[0]  # Assume first argument is ID
                
                # Log the action
                audit_tracker.log_action(
                    action=action,
                    table_name=table_name,
                    record_id=record_id,
                    user_info={'function': func.__name__}
                )
                
                return result
                
            except Exception as e:
                # Log the error attempt
                audit_tracker.log_action(
                    action=f"{action}_ERROR",
                    table_name=table_name,
                    record_id=record_id if 'record_id' in locals() else 'unknown',
                    user_info={'function': func.__name__, 'error': str(e)}
                )
                raise
        
        return wrapper
    return decorator

# Context manager for transaction-level auditing
@contextmanager
def audit_transaction(description, user_info=None):
    """Context manager for auditing complete transactions"""
    start_time = datetime.now()
    transaction_id = f"TXN_{start_time.strftime('%Y%m%d_%H%M%S_%f')}"
    
    try:
        audit_tracker.log_action(
            action="TRANSACTION_START",
            table_name="SYSTEM",
            record_id=transaction_id,
            user_info={
                'description': description,
                'user_info': user_info,
                'start_time': start_time.isoformat()
            }
        )
        
        yield transaction_id
        
        # Log successful completion
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        audit_tracker.log_action(
            action="TRANSACTION_COMPLETE",
            table_name="SYSTEM",
            record_id=transaction_id,
            user_info={
                'description': description,
                'duration_seconds': duration,
                'end_time': end_time.isoformat()
            }
        )
        
    except Exception as e:
        # Log failed transaction
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        audit_tracker.log_action(
            action="TRANSACTION_ERROR",
            table_name="SYSTEM",
            record_id=transaction_id,
            user_info={
                'description': description,
                'error': str(e),
                'duration_seconds': duration,
                'end_time': end_time.isoformat()
            }
        )
        raise
