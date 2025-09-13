# 🚀 Enhanced Discord Logging System

## Overview
The enhanced Discord logging system provides comprehensive real-time monitoring and logging to Discord channels via webhooks. It includes advanced features like retry mechanisms, offline queuing, Flask request context integration, performance monitoring, and configurable feature toggles.

## 🏗️ Architecture

### 4-Channel System
- **💰 Finance Channel**: Invoice creation, payments, BTW calculations, high-value transaction alerts
- **🔧 System Channel**: Application startup/shutdown, database operations, performance warnings
- **🚨 Errors Channel**: Application errors, validation errors, critical system failures
- **📊 Activity Channel**: User actions, file operations, general activity tracking

### Key Features
- **Environment-based Configuration**: Secure webhook management via environment variables
- **Retry Mechanism**: Automatic retry with exponential backoff for failed webhook requests
- **Offline Queuing**: Message queuing when Discord is unavailable
- **Flask Context Integration**: Automatic capture of request details, IP addresses, user agents
- **Performance Monitoring**: Automatic detection of slow functions and operations
- **Feature Toggles**: Granular control over what gets logged
- **Rate Limiting**: Protection against Discord rate limits

## 🔧 Configuration

### Environment Variables
Create a `.env` file (copy from `.env.example`):

```env
# Discord Webhook URLs
DISCORD_WEBHOOK_FINANCE=https://discord.com/api/webhooks/YOUR_FINANCE_WEBHOOK
DISCORD_WEBHOOK_SYSTEM=https://discord.com/api/webhooks/YOUR_SYSTEM_WEBHOOK
DISCORD_WEBHOOK_ERRORS=https://discord.com/api/webhooks/YOUR_ERRORS_WEBHOOK
DISCORD_WEBHOOK_ACTIVITY=https://discord.com/api/webhooks/YOUR_ACTIVITY_WEBHOOK

# Logging Settings
DISCORD_LOGGING_ENABLED=True
DISCORD_RATE_LIMIT=10
DISCORD_RETRY_ATTEMPTS=3
DISCORD_RETRY_DELAY=1.0
DISCORD_TIMEOUT=10
DISCORD_QUEUE_SIZE=100

# Feature Toggles
DISCORD_LOG_FINANCE=True
DISCORD_LOG_SYSTEM=True
DISCORD_LOG_ERRORS=True
DISCORD_LOG_ACTIVITY=True
DISCORD_LOG_PERFORMANCE=True
DISCORD_LOG_SUMMARIES=True
```

### Discord Setup
1. Create Discord server with 4 channels: `💰-finance-logs`, `🔧-system-logs`, `🚨-errors-debug`, `📊-user-activity`
2. Create webhook for each channel
3. Copy webhook URLs to environment variables

## 📝 Usage

### Basic Logging
```python
from discord_logger import discord_logger

# Log invoice creation
discord_logger.log_invoice_created("INV001", 1500.00, "Client Name")

# Log system events
discord_logger.log_system_event("Database Backup", "Scheduled backup completed")

# Log user actions
discord_logger.log_user_action("Invoice Generated", details={"invoice_id": "INV001"})

# Log errors
try:
    risky_operation()
except Exception as e:
    discord_logger.log_error(e, context="Invoice Processing")
```

### Decorators
```python
from discord_logger import log_errors, log_activity, log_performance

@log_errors(context="Invoice Processing")
@log_activity(action="Create Invoice")
@log_performance(threshold_seconds=2.0)
def create_invoice(invoice_data):
    # Function implementation
    pass
```

### Available Decorators
- **`@log_errors(context="Optional Context")`**: Automatically logs any exceptions
- **`@log_activity(action="Action Name")`**: Logs function calls and results
- **`@log_performance(threshold_seconds=1.0)`**: Logs slow function execution

## 📊 Message Types

### Finance Logs
- Invoice creation/updates
- Payment processing
- BTW calculations
- High-value transaction alerts (configurable threshold)

### System Logs
- Application startup/shutdown
- Database operations
- Performance warnings
- File operations

### Error Logs
- Application exceptions with stack traces
- Validation errors
- Critical system failures
- Context-aware error reporting

### Activity Logs
- User actions with IP tracking
- File uploads/downloads
- Form submissions
- Request details (method, endpoint, user agent)

## 🔍 Request Context Integration

The system automatically captures Flask request context when available:
- Request method (GET, POST, etc.)
- Endpoint name
- Client IP address
- User agent
- Referrer
- Session information

## ⚡ Performance Monitoring

### Automatic Performance Logging
Functions decorated with `@log_performance` will automatically log warnings when execution time exceeds the threshold.

### Manual Performance Warnings
```python
discord_logger.log_performance_warning(
    metric="Database Query Time",
    value=2.5,
    threshold=1.0,
    unit="s"
)
```

## 🔄 Retry & Reliability

### Retry Mechanism
- Failed webhook requests are automatically retried
- Configurable retry attempts and delays
- Exponential backoff for repeated failures

### Offline Queuing
- Messages are queued when Discord is unavailable
- Background worker processes the queue
- Configurable queue size to prevent memory issues

### Fallback Logging
- Failed Discord messages fall back to Python logging
- Critical errors are always logged locally

## 🎛️ Feature Toggles

Control what gets logged via environment variables:
- `DISCORD_LOG_FINANCE`: Finance-related events
- `DISCORD_LOG_SYSTEM`: System events
- `DISCORD_LOG_ERRORS`: Error logging
- `DISCORD_LOG_ACTIVITY`: User activity tracking
- `DISCORD_LOG_PERFORMANCE`: Performance warnings
- `DISCORD_LOG_SUMMARIES`: Daily summary reports

## 🧪 Testing

Run the test script to verify functionality:
```bash
python test_discord_logger.py
```

This will test all logging features and send test messages to your Discord channels.

## 🛡️ Security

### Best Practices
- Store webhook URLs in environment variables, not code
- Use different webhooks for development and production
- Regularly rotate webhook URLs if compromised
- Monitor Discord channels for unauthorized access

### Data Sanitization
- Sensitive data is automatically truncated
- Personal information is filtered from logs
- IP addresses are logged for security but can be disabled

## 📈 Monitoring & Maintenance

### Health Monitoring
The system includes built-in health monitoring:
- Webhook success/failure rates
- Queue size monitoring
- Rate limit tracking

### Maintenance Tasks
- Regular webhook URL rotation
- Log retention management
- Performance optimization

## 🔮 Future Enhancements

Planned improvements:
- Webhook health dashboard
- Advanced analytics and reporting
- Integration with external monitoring tools
- Custom alert rules and notifications
- Log aggregation and search capabilities

## 📞 Support

For issues or questions:
1. Check Discord channels for error messages
2. Review local logs for fallback messages
3. Verify webhook URLs are correct
4. Test with `test_discord_logger.py`
