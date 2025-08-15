"""
Standalone Audit Viewer Application
Separate Flask app running on port 5001 for viewing audit logs
"""

from flask import Flask, render_template, request, jsonify
import sqlite3
import json
from datetime import datetime, timedelta
from audit_tracker import AuditTracker

app = Flask(__name__, template_folder='audit_templates')
app.secret_key = 'audit_viewer_secret_key_2024'

# Add built-in functions to Jinja2 environment
def get_pagination_url(page):
    """Generate pagination URL with current filters"""
    args = request.args.copy()
    args['page'] = page
    return '&'.join([f"{k}={v}" for k, v in args.items() if v])

app.jinja_env.globals.update({
    'max': max,
    'min': min,
    'range': range,
    'len': len,
    'get_pagination_url': get_pagination_url
})

# Initialize audit tracker
audit_tracker = AuditTracker()

@app.route('/')
def dashboard():
    """Main audit dashboard with statistics and recent activity"""
    try:
        # Get statistics
        stats = audit_tracker.get_statistics()
        
        # Get recent logs (last 50)
        recent_logs = audit_tracker.get_audit_logs(limit=50)
        
        # Format logs for display
        formatted_logs = []
        for log in recent_logs:
            log_dict = dict(log)
            
            # Parse JSON fields
            if log_dict['changes']:
                try:
                    log_dict['changes'] = json.loads(log_dict['changes'])
                except:
                    pass
            
            if log_dict['old_values']:
                try:
                    log_dict['old_values'] = json.loads(log_dict['old_values'])
                except:
                    pass
            
            if log_dict['new_values']:
                try:
                    log_dict['new_values'] = json.loads(log_dict['new_values'])
                except:
                    pass
            
            if log_dict['user_info']:
                try:
                    log_dict['user_info'] = json.loads(log_dict['user_info'])
                except:
                    pass
            
            formatted_logs.append(log_dict)
        
        return render_template('audit_dashboard.html', 
                             stats=stats, 
                             recent_logs=formatted_logs)
        
    except Exception as e:
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/logs')
def view_logs():
    """View audit logs with filtering"""
    # Get filter parameters
    table_name = request.args.get('table')
    action = request.args.get('action')
    record_id = request.args.get('record_id')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 50))
    
    # Calculate offset
    offset = (page - 1) * per_page
    
    try:
        # Get filtered logs
        logs = audit_tracker.get_audit_logs(
            table_name=table_name,
            action=action,
            record_id=record_id,
            date_from=date_from,
            date_to=date_to,
            limit=per_page,
            offset=offset
        )
        
        # Get total count for pagination
        with sqlite3.connect(audit_tracker.audit_db_path) as conn:
            cursor = conn.cursor()
            
            # Build count query with same filters
            count_query = "SELECT COUNT(*) FROM audit_log WHERE 1=1"
            params = []
            
            if table_name:
                count_query += " AND table_name = ?"
                params.append(table_name)
            if action:
                count_query += " AND action = ?"
                params.append(action)
            if record_id:
                count_query += " AND record_id = ?"
                params.append(record_id)
            if date_from:
                count_query += " AND DATE(timestamp) >= ?"
                params.append(date_from)
            if date_to:
                count_query += " AND DATE(timestamp) <= ?"
                params.append(date_to)
            
            cursor.execute(count_query, params)
            total_count = cursor.fetchone()[0]
        
        # Calculate pagination info
        total_pages = max(1, (total_count + per_page - 1) // per_page)
        has_prev = page > 1
        has_next = page < total_pages
        
        # Format logs for display
        formatted_logs = []
        for log in logs:
            log_dict = dict(log)
            
            # Parse JSON fields
            if log_dict['changes']:
                try:
                    log_dict['changes'] = json.loads(log_dict['changes'])
                except:
                    pass
            
            if log_dict['old_values']:
                try:
                    log_dict['old_values'] = json.loads(log_dict['old_values'])
                except:
                    pass
            
            if log_dict['new_values']:
                try:
                    log_dict['new_values'] = json.loads(log_dict['new_values'])
                except:
                    pass
            
            if log_dict['user_info']:
                try:
                    log_dict['user_info'] = json.loads(log_dict['user_info'])
                except:
                    pass
            
            formatted_logs.append(log_dict)
        
        # Get available tables and actions for filter dropdowns
        with sqlite3.connect(audit_tracker.audit_db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT DISTINCT table_name FROM audit_log ORDER BY table_name")
            tables = [row[0] for row in cursor.fetchall()]
            
            cursor.execute("SELECT DISTINCT action FROM audit_log ORDER BY action")
            actions = [row[0] for row in cursor.fetchall()]
        
        return render_template('audit_logs.html',
                             logs=formatted_logs,
                             tables=tables,
                             actions=actions,
                             current_filters={
                                 'table': table_name,
                                 'action': action,
                                 'record_id': record_id,
                                 'date_from': date_from,
                                 'date_to': date_to,
                                 'page': page,
                                 'per_page': per_page
                             },
                             pagination={
                                 'total_count': total_count,
                                 'total_pages': total_pages,
                                 'has_prev': has_prev,
                                 'has_next': has_next,
                                 'current_page': page
                             })
        
    except Exception as e:
        return f"Error loading logs: {str(e)}", 500

@app.route('/record/<table_name>/<record_id>')
def record_history(table_name, record_id):
    """View complete history for a specific record"""
    try:
        history = audit_tracker.get_record_history(table_name, record_id)
        
        # Format history for display
        formatted_history = []
        for log in history:
            log_dict = dict(log)
            
            # Parse JSON fields
            if log_dict['changes']:
                try:
                    log_dict['changes'] = json.loads(log_dict['changes'])
                except:
                    pass
            
            if log_dict['old_values']:
                try:
                    log_dict['old_values'] = json.loads(log_dict['old_values'])
                except:
                    pass
            
            if log_dict['new_values']:
                try:
                    log_dict['new_values'] = json.loads(log_dict['new_values'])
                except:
                    pass
            
            if log_dict['user_info']:
                try:
                    log_dict['user_info'] = json.loads(log_dict['user_info'])
                except:
                    pass
            
            formatted_history.append(log_dict)
        
        return render_template('record_history.html',
                             history=formatted_history,
                             table_name=table_name,
                             record_id=record_id)
        
    except Exception as e:
        return f"Error loading record history: {str(e)}", 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for statistics (for AJAX updates)"""
    try:
        stats = audit_tracker.get_statistics()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent/<int:limit>')
def api_recent_logs(limit=10):
    """API endpoint for recent logs"""
    try:
        logs = audit_tracker.get_audit_logs(limit=limit)
        
        # Convert to list of dicts
        log_list = []
        for log in logs:
            log_dict = dict(log)
            
            # Parse JSON fields
            for field in ['changes', 'old_values', 'new_values', 'user_info']:
                if log_dict[field]:
                    try:
                        log_dict[field] = json.loads(log_dict[field])
                    except:
                        pass
            
            log_list.append(log_dict)
        
        return jsonify(log_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/search')
def search_logs():
    """Advanced search interface"""
    return render_template('audit_search.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    """API endpoint for advanced search"""
    try:
        data = request.get_json()
        
        # Extract search parameters
        table_name = data.get('table_name')
        action = data.get('action')
        record_id = data.get('record_id')
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        search_text = data.get('search_text')
        limit = data.get('limit', 100)
        
        # Perform search
        logs = audit_tracker.get_audit_logs(
            table_name=table_name,
            action=action,
            record_id=record_id,
            date_from=date_from,
            date_to=date_to,
            limit=limit
        )
        
        # Convert to list and filter by search text if provided
        log_list = []
        for log in logs:
            log_dict = dict(log)
            
            # Parse JSON fields
            for field in ['changes', 'old_values', 'new_values', 'user_info']:
                if log_dict[field]:
                    try:
                        log_dict[field] = json.loads(log_dict[field])
                    except:
                        pass
            
            # Text search in all fields if search_text provided
            if search_text:
                log_text = json.dumps(log_dict, default=str).lower()
                if search_text.lower() not in log_text:
                    continue
            
            log_list.append(log_dict)
        
        return jsonify(log_list)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/export')
def export_logs():
    """Export audit logs to CSV/JSON"""
    format_type = request.args.get('format', 'json')
    
    try:
        # Get all logs (or filtered if parameters provided)
        table_name = request.args.get('table')
        action = request.args.get('action')
        date_from = request.args.get('date_from')
        date_to = request.args.get('date_to')
        
        logs = audit_tracker.get_audit_logs(
            table_name=table_name,
            action=action,
            date_from=date_from,
            date_to=date_to,
            limit=10000  # Large limit for export
        )
        
        if format_type == 'json':
            # Convert to JSON
            log_list = []
            for log in logs:
                log_dict = dict(log)
                
                # Parse JSON fields
                for field in ['changes', 'old_values', 'new_values', 'user_info']:
                    if log_dict[field]:
                        try:
                            log_dict[field] = json.loads(log_dict[field])
                        except:
                            pass
                
                log_list.append(log_dict)
            
            response = jsonify(log_list)
            response.headers['Content-Disposition'] = f'attachment; filename=audit_logs_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            return response
        
        else:
            return "CSV export not implemented yet", 501
            
    except Exception as e:
        return f"Error exporting logs: {str(e)}", 500

if __name__ == '__main__':
    print("Starting Audit Viewer Application...")
    print("Access the audit dashboard at: http://localhost:5001")
    print("Press Ctrl+C to stop the server")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
