"""
Discord Logging System for Ozark Finances
Provides real-time monitoring and logging to Discord channels via webhooks
"""

import requests
import json
import logging
import asyncio
from datetime import datetime, timezone
from typing import Dict, Optional, Any, List
import traceback
from functools import wraps
import os
import time
import threading
from queue import Queue, Empty
from flask import request, session, g, has_request_context
from config import Config

class DiscordLogger:
    """Main Discord logging class with support for multiple channels"""
    
    def __init__(self):
        # Load configuration
        self.config = Config()
        
        # Webhook URLs from configuration
        self.webhooks = self.config.DISCORD_WEBHOOKS
        
        # Color codes for different message types
        self.colors = {
            'success': 0x00FF00,   # Green
            'info': 0x0099FF,      # Blue
            'warning': 0xFFAA00,   # Orange
            'error': 0xFF0000,     # Red
            'critical': 0x990000,  # Dark Red
            'finance': 0x00AA00,   # Dark Green
            'system': 0x6666FF,    # Purple
            'user': 0xFF6600       # Orange
        }
        
        # Event emojis
        self.emojis = {
            'invoice_created': '📄',
            'invoice_paid': '💰',
            'invoice_edited': '✏️',
            'payment_processed': '💳',
            'btw_calculated': '🏛️',
            'import_success': '📥',
            'import_failed': '❌',
            'export_success': '📤',
            'user_login': '🔑',
            'user_logout': '🚪',
            'error': '🚨',
            'warning': '⚠️',
            'system_start': '🟢',
            'system_stop': '🔴',
            'database': '🗄️',
            'performance': '📊'
        }
        
        # Configuration from config.py
        self.enabled = self.config.DISCORD_LOGGING_ENABLED
        self.rate_limit = self.config.DISCORD_RATE_LIMIT
        self.features = self.config.DISCORD_LOG_FEATURES
        self.retry_attempts = self.config.DISCORD_RETRY_ATTEMPTS
        self.retry_delay = self.config.DISCORD_RETRY_DELAY
        self.timeout = self.config.DISCORD_TIMEOUT
        
        # Rate limiting
        self.message_count = 0
        self.last_reset = datetime.now()
        
        # Message queue for offline reliability
        self.message_queue = Queue(maxsize=self.config.DISCORD_QUEUE_SIZE)
        self.queue_worker_running = False
        self._start_queue_worker()
        
    def _start_queue_worker(self):
        """Start background thread to process message queue"""
        if not self.queue_worker_running:
            self.queue_worker_running = True
            worker_thread = threading.Thread(target=self._queue_worker, daemon=True)
            worker_thread.start()
    
    def _queue_worker(self):
        """Background worker to process queued messages"""
        while self.queue_worker_running:
            try:
                # Get message from queue with timeout
                webhook_url, embed, username, retries = self.message_queue.get(timeout=1)
                
                # Try to send the message
                success = self._send_webhook_direct(webhook_url, embed, username)
                
                if not success and retries > 0:
                    # Re-queue with fewer retries
                    try:
                        self.message_queue.put_nowait((webhook_url, embed, username, retries - 1))
                    except:
                        pass  # Queue full, drop message
                        
                self.message_queue.task_done()
                
            except Empty:
                continue
            except Exception as e:
                logging.error(f"Queue worker error: {e}")
    
    def _get_request_context(self) -> Dict[str, Any]:
        """Extract context information from Flask request"""
        context = {}
        
        if has_request_context():
            try:
                # Request information
                context['method'] = request.method
                context['endpoint'] = request.endpoint
                context['url'] = request.url
                context['remote_addr'] = request.remote_addr
                context['user_agent'] = request.headers.get('User-Agent', 'Unknown')[:100]
                
                # Session information
                if session:
                    context['session_id'] = session.get('_permanent', 'temp')
                    
                # Additional headers
                context['referer'] = request.headers.get('Referer', 'Direct')[:100]
                context['content_type'] = request.headers.get('Content-Type', 'N/A')
                
            except Exception as e:
                context['context_error'] = str(e)
                
        return context
        
    def _check_rate_limit(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        if (now - self.last_reset).seconds >= 60:
            self.message_count = 0
            self.last_reset = now
            
        if self.message_count >= self.rate_limit:
            return False
            
        self.message_count += 1
        return True
    
    def _create_embed(self, title: str, description: str = None, color: int = None, 
                     fields: list = None, footer: str = None) -> dict:
        """Create a Discord embed message"""
        embed = {
            "title": title,
            "color": color or self.colors['info'],
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        
        if description:
            embed["description"] = description
            
        if fields:
            embed["fields"] = fields
            
        if footer:
            embed["footer"] = {"text": footer}
        else:
            embed["footer"] = {"text": "Ozark Finances • Flask App"}
            
        return embed
    
    def _send_webhook(self, webhook_url: str, embed: dict, username: str = None) -> bool:
        """Send message to Discord webhook with retry and queueing"""
        if not self.enabled or not self._check_rate_limit():
            return False
            
        # Try immediate send first
        success = self._send_webhook_direct(webhook_url, embed, username)
        
        if not success:
            # Queue for retry
            try:
                self.message_queue.put_nowait((webhook_url, embed, username, self.retry_attempts))
            except:
                # Queue full, log to file as fallback
                logging.error("Discord queue full, message dropped")
                
        return success
    
    def _send_webhook_direct(self, webhook_url: str, embed: dict, username: str = None) -> bool:
        """Send message directly to Discord webhook"""
        try:
            payload = {
                "embeds": [embed],
                "username": username or "Ozark Finances"
            }
            
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=self.timeout
            )
            
            return response.status_code == 204
            
        except Exception as e:
            # Log to file as fallback
            logging.error(f"Discord webhook failed: {e}")
            return False
    
    # ===== FINANCE LOGGING =====
    
    def log_invoice_created(self, invoice_id: str, amount: float, client: str = None):
        """Log new invoice creation"""
        if not self.features.get('finance_events', True):
            return
            
        fields = [
            {"name": "Invoice ID", "value": f"#{invoice_id}", "inline": True},
            {"name": "Amount", "value": f"€{amount:,.2f}", "inline": True},
            {"name": "Status", "value": "Pending", "inline": True}
        ]
        
        if client:
            fields.append({"name": "Client", "value": client, "inline": False})
        
        # Add request context
        context = self._get_request_context()
        if context.get('remote_addr'):
            fields.append({"name": "IP Address", "value": context['remote_addr'], "inline": True})
            
        embed = self._create_embed(
            title=f"{self.emojis['invoice_created']} New Invoice Created",
            color=self.colors['finance'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['finance'], embed)
    
    def log_invoice_paid(self, invoice_id: str, amount: float, payment_date: str = None):
        """Log invoice payment"""
        fields = [
            {"name": "Invoice ID", "value": f"#{invoice_id}", "inline": True},
            {"name": "Amount", "value": f"€{amount:,.2f}", "inline": True},
            {"name": "Payment Date", "value": payment_date or "Today", "inline": True}
        ]
        
        embed = self._create_embed(
            title=f"{self.emojis['invoice_paid']} Invoice Paid",
            color=self.colors['success'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['finance'], embed)
    
    def log_btw_payment(self, quarter: str, amount: float, status: str):
        """Log BTW quarterly payment"""
        fields = [
            {"name": "Quarter", "value": quarter, "inline": True},
            {"name": "Amount", "value": f"€{amount:,.2f}", "inline": True},
            {"name": "Status", "value": status.title(), "inline": True}
        ]
        
        color = self.colors['success'] if status == 'paid' else self.colors['warning']
        
        embed = self._create_embed(
            title=f"{self.emojis['btw_calculated']} BTW Payment Update",
            color=color,
            fields=fields
        )
        
        self._send_webhook(self.webhooks['finance'], embed)
    
    def log_large_transaction(self, invoice_id: str, amount: float, threshold: float = 5000):
        """Log high-value transactions"""
        if amount < threshold:
            return
            
        fields = [
            {"name": "Invoice ID", "value": f"#{invoice_id}", "inline": True},
            {"name": "Amount", "value": f"€{amount:,.2f}", "inline": True},
            {"name": "Threshold", "value": f"€{threshold:,.2f}", "inline": True}
        ]
        
        embed = self._create_embed(
            title=f"💎 High-Value Transaction Alert",
            description=f"⚠️ Amount exceeds threshold of €{threshold:,.2f}",
            color=self.colors['warning'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['finance'], embed)
    
    # ===== SYSTEM LOGGING =====
    
    def log_app_startup(self, version: str = None, host: str = None, port: int = None):
        """Log application startup"""
        fields = [
            {"name": "Status", "value": "Online", "inline": True},
            {"name": "Host", "value": host or "localhost", "inline": True},
            {"name": "Port", "value": str(port) if port else "5000", "inline": True}
        ]
        
        if version:
            fields.append({"name": "Version", "value": version, "inline": True})
            
        embed = self._create_embed(
            title=f"{self.emojis['system_start']} Application Started",
            color=self.colors['success'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['system'], embed)
    
    def log_app_shutdown(self, reason: str = None):
        """Log application shutdown"""
        fields = [
            {"name": "Status", "value": "Offline", "inline": True},
            {"name": "Uptime", "value": "Not tracked", "inline": True}
        ]
        
        if reason:
            fields.append({"name": "Reason", "value": reason, "inline": False})
            
        embed = self._create_embed(
            title=f"{self.emojis['system_stop']} Application Stopped",
            color=self.colors['warning'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['system'], embed)
    
    def log_database_operation(self, operation: str, table: str = None, count: int = None, duration: float = None):
        """Log database operations"""
        fields = [
            {"name": "Operation", "value": operation, "inline": True}
        ]
        
        if table:
            fields.append({"name": "Table", "value": table, "inline": True})
        if count is not None:
            fields.append({"name": "Records", "value": str(count), "inline": True})
        if duration is not None:
            fields.append({"name": "Duration", "value": f"{duration:.2f}s", "inline": True})
            
        embed = self._create_embed(
            title=f"{self.emojis['database']} Database Operation",
            color=self.colors['system'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['system'], embed)
    
    def log_performance_warning(self, metric: str, value: float, threshold: float, unit: str = ""):
        """Log performance warnings"""
        fields = [
            {"name": "Metric", "value": metric, "inline": True},
            {"name": "Current", "value": f"{value:.2f}{unit}", "inline": True},
            {"name": "Threshold", "value": f"{threshold:.2f}{unit}", "inline": True}
        ]
        
        embed = self._create_embed(
            title=f"{self.emojis['performance']} Performance Warning",
            description=f"⚠️ {metric} has exceeded the threshold",
            color=self.colors['warning'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['system'], embed)
    
    def log_system_event(self, event: str, description: str = None, details: dict = None):
        """Log general system events"""
        fields = [
            {"name": "Event", "value": event, "inline": True}
        ]
        
        if description:
            fields.append({"name": "Description", "value": description, "inline": False})
            
        if details:
            for key, value in details.items():
                fields.append({"name": key.title(), "value": str(value), "inline": True})
        
        embed = self._create_embed(
            title=f"{self.emojis['system_start']} System Event",
            color=self.colors['system'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['system'], embed)
    
    # ===== ERROR LOGGING =====
    
    def log_error(self, error: Exception, context: str = None, user: str = None, 
                 file_name: str = None, line_number: int = None):
        """Log application errors"""
        if not self.features.get('error_events', True):
            return
            
        fields = [
            {"name": "Error Type", "value": type(error).__name__, "inline": True},
            {"name": "Message", "value": str(error)[:100], "inline": False}
        ]
        
        if context:
            fields.append({"name": "Context", "value": context, "inline": True})
        if user:
            fields.append({"name": "User", "value": user, "inline": True})
        if file_name:
            location = f"{file_name}"
            if line_number:
                location += f":{line_number}"
            fields.append({"name": "Location", "value": location, "inline": True})
        
        # Add request context
        request_context = self._get_request_context()
        if request_context.get('remote_addr'):
            fields.append({"name": "IP Address", "value": request_context['remote_addr'], "inline": True})
        if request_context.get('endpoint'):
            fields.append({"name": "Endpoint", "value": request_context['endpoint'], "inline": True})
        if request_context.get('method'):
            fields.append({"name": "Method", "value": request_context['method'], "inline": True})
            
        # Add stack trace (first 3 lines)
        tb_lines = traceback.format_tb(error.__traceback__)
        if tb_lines:
            stack_preview = "\\n".join(tb_lines[:3])
            fields.append({"name": "Stack Trace", "value": f"```{stack_preview[:500]}```", "inline": False})
        
        embed = self._create_embed(
            title=f"{self.emojis['error']} Application Error",
            color=self.colors['error'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['errors'], embed)
    
    def log_validation_error(self, form_name: str, field: str, error_message: str, user: str = None):
        """Log form validation errors"""
        fields = [
            {"name": "Form", "value": form_name, "inline": True},
            {"name": "Field", "value": field, "inline": True},
            {"name": "Error", "value": error_message, "inline": False}
        ]
        
        if user:
            fields.append({"name": "User", "value": user, "inline": True})
            
        embed = self._create_embed(
            title=f"{self.emojis['warning']} Validation Error",
            color=self.colors['warning'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['errors'], embed)
    
    def log_critical_error(self, message: str, details: str = None):
        """Log critical system errors"""
        fields = [
            {"name": "Severity", "value": "CRITICAL", "inline": True},
            {"name": "Message", "value": message, "inline": False}
        ]
        
        if details:
            fields.append({"name": "Details", "value": details[:500], "inline": False})
            
        embed = self._create_embed(
            title=f"💥 CRITICAL ERROR",
            description="🚨 **Immediate attention required!**",
            color=self.colors['critical'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['errors'], embed)
    
    # ===== USER ACTIVITY LOGGING =====
    
    def log_user_action(self, action: str, user: str = None, details: dict = None, ip: str = None):
        """Log user activities"""
        if not self.features.get('user_activity', True):
            return
            
        fields = [
            {"name": "Action", "value": action, "inline": True}
        ]
        
        # Auto-detect request context if not provided
        context = self._get_request_context()
        
        if user:
            fields.append({"name": "User", "value": user, "inline": True})
        
        # Use provided IP or auto-detect
        user_ip = ip or context.get('remote_addr')
        if user_ip:
            fields.append({"name": "IP Address", "value": user_ip, "inline": True})
        
        # Add request details
        if context.get('method'):
            fields.append({"name": "Method", "value": context['method'], "inline": True})
        if context.get('endpoint'):
            fields.append({"name": "Endpoint", "value": context['endpoint'], "inline": True})
        if context.get('user_agent'):
            fields.append({"name": "User Agent", "value": context['user_agent'][:50], "inline": False})
            
        if details:
            for key, value in details.items():
                fields.append({"name": key.title(), "value": str(value)[:100], "inline": True})
        
        embed = self._create_embed(
            title=f"{self.emojis['user_login']} User Activity",
            color=self.colors['user'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['activity'], embed)
    
    def log_file_operation(self, operation: str, filename: str, success: bool, 
                          file_size: int = None, processing_time: float = None, error: str = None):
        """Log file upload/download operations"""
        status = "Success" if success else "Failed"
        color = self.colors['success'] if success else self.colors['error']
        emoji = self.emojis['import_success'] if success else self.emojis['import_failed']
        
        fields = [
            {"name": "Operation", "value": operation, "inline": True},
            {"name": "Filename", "value": filename, "inline": True},
            {"name": "Status", "value": status, "inline": True}
        ]
        
        if file_size:
            fields.append({"name": "File Size", "value": f"{file_size:,} bytes", "inline": True})
        if processing_time:
            fields.append({"name": "Processing Time", "value": f"{processing_time:.2f}s", "inline": True})
        if error:
            fields.append({"name": "Error", "value": error[:200], "inline": False})
            
        embed = self._create_embed(
            title=f"{emoji} File {operation.title()}",
            color=color,
            fields=fields
        )
        
        self._send_webhook(self.webhooks['activity'], embed)
    
    def log_daily_summary(self, stats: dict):
        """Send daily summary report"""
        fields = []
        
        if 'invoices' in stats:
            invoice_stats = stats['invoices']
            fields.append({
                "name": "📄 Invoices",
                "value": f"Created: {invoice_stats.get('created', 0)}\\nPaid: {invoice_stats.get('paid', 0)}\\nPending: {invoice_stats.get('pending', 0)}",
                "inline": True
            })
        
        if 'revenue' in stats:
            revenue_stats = stats['revenue']
            fields.append({
                "name": "💰 Revenue",
                "value": f"Today: €{revenue_stats.get('today', 0):,.2f}\\nMonth: €{revenue_stats.get('month', 0):,.2f}",
                "inline": True
            })
        
        if 'system' in stats:
            system_stats = stats['system']
            fields.append({
                "name": "🔧 System",
                "value": f"Uptime: {system_stats.get('uptime', 'N/A')}\\nResponse: {system_stats.get('avg_response', 'N/A')}",
                "inline": True
            })
        
        embed = self._create_embed(
            title=f"{self.emojis['performance']} Daily Summary Report",
            description=f"Summary for {datetime.now().strftime('%Y-%m-%d')}",
            color=self.colors['info'],
            fields=fields
        )
        
        self._send_webhook(self.webhooks['system'], embed)

# Global instance
discord_logger = DiscordLogger()

# Decorator for automatic error logging
def log_errors(context: str = None, channel: str = 'errors'):
    """Decorator to automatically log function errors"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # Get additional context
                error_context = context or f"Function: {func.__name__}"
                
                discord_logger.log_error(
                    error=e,
                    context=error_context,
                    file_name=func.__code__.co_filename,
                    line_number=func.__code__.co_firstlineno
                )
                raise
        return wrapper
    return decorator

# Decorator for logging function calls
def log_activity(action: str = None, channel: str = 'activity', log_success: bool = True, log_failure: bool = True):
    """Decorator to log function calls as user activity"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            activity_name = action or f"{func.__name__}"
            
            try:
                result = func(*args, **kwargs)
                
                if log_success:
                    discord_logger.log_user_action(
                        action=f"{activity_name} - Success",
                        details={"function": func.__name__, "status": "success"}
                    )
                return result
                
            except Exception as e:
                if log_failure:
                    discord_logger.log_user_action(
                        action=f"{activity_name} - Failed",
                        details={"function": func.__name__, "status": "failed", "error": str(e)[:100]}
                    )
                raise
        return wrapper
    return decorator

# Decorator for performance monitoring
def log_performance(threshold_seconds: float = 1.0):
    """Decorator to log slow function execution"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                
                if execution_time > threshold_seconds:
                    discord_logger.log_performance_warning(
                        metric=f"Function Execution Time: {func.__name__}",
                        value=execution_time,
                        threshold=threshold_seconds,
                        unit="s"
                    )
                
                return result
                
            except Exception as e:
                execution_time = time.time() - start_time
                discord_logger.log_error(
                    error=e,
                    context=f"Performance monitored function: {func.__name__} (took {execution_time:.2f}s)"
                )
                raise
                
        return wrapper
    return decorator
