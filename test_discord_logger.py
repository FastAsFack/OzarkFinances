"""
Discord Logger Test Script
Tests all the enhanced Discord logging functionality
"""

from discord_logger import discord_logger, log_errors, log_activity, log_performance
import time
import traceback

def test_basic_logging():
    """Test basic logging functionality"""
    print("Testing basic Discord logging...")
    
    # Test system event
    discord_logger.log_system_event("Test System Event", "Testing enhanced logging system")
    
    # Test invoice creation
    discord_logger.log_invoice_created("TEST001", 1500.00, "Test Client")
    
    # Test BTW payment
    discord_logger.log_btw_payment("Q1 2025", 315.50, "pending")
    
    # Test user action
    discord_logger.log_user_action("Manual Test", details={"test_type": "basic_functionality"})
    
    print("Basic logging tests completed!")

def test_error_logging():
    """Test error logging functionality"""
    print("Testing error logging...")
    
    try:
        # Intentionally cause an error
        raise ValueError("This is a test error for Discord logging")
    except Exception as e:
        discord_logger.log_error(e, context="Test Error Context")
    
    # Test validation error
    discord_logger.log_validation_error("test_form", "test_field", "Test validation message")
    
    # Test critical error
    discord_logger.log_critical_error("Test Critical Error", "This is a test critical error")
    
    print("Error logging tests completed!")

@log_errors(context="Decorator Test")
@log_activity(action="Test Decorator Function")
@log_performance(threshold_seconds=0.1)
def test_decorator_function():
    """Test function with all decorators"""
    print("Testing decorator functionality...")
    time.sleep(0.2)  # Simulate slow operation for performance logging
    
    # This should trigger performance warning
    return "Decorator test completed"

@log_errors(context="Error Decorator Test")
def test_error_decorator():
    """Test error decorator"""
    print("Testing error decorator...")
    raise RuntimeError("Test error from decorator")

def test_performance_monitoring():
    """Test performance monitoring"""
    print("Testing performance monitoring...")
    
    discord_logger.log_performance_warning(
        metric="Test Response Time",
        value=2.5,
        threshold=1.0,
        unit="s"
    )
    
    print("Performance monitoring tests completed!")

def test_file_operations():
    """Test file operation logging"""
    print("Testing file operation logging...")
    
    discord_logger.log_file_operation(
        operation="upload",
        filename="test_template.xlsx",
        success=True,
        file_size=15432,
        processing_time=0.85
    )
    
    discord_logger.log_file_operation(
        operation="download",
        filename="failed_file.xlsx",
        success=False,
        error="File not found"
    )
    
    print("File operation tests completed!")

def test_large_transaction_alert():
    """Test large transaction alerting"""
    print("Testing large transaction alerts...")
    
    # This should trigger an alert
    discord_logger.log_large_transaction("LARGE001", 6500.00, threshold=5000.00)
    
    # This should not trigger an alert
    discord_logger.log_large_transaction("SMALL001", 3500.00, threshold=5000.00)
    
    print("Large transaction tests completed!")

def main():
    """Run all Discord logging tests"""
    print("=== Discord Logger Enhanced Testing ===\\n")
    
    try:
        test_basic_logging()
        print()
        
        test_error_logging()
        print()
        
        result = test_decorator_function()
        print(f"Decorator result: {result}")
        print()
        
        test_performance_monitoring()
        print()
        
        test_file_operations()
        print()
        
        test_large_transaction_alert()
        print()
        
        # Test error decorator
        try:
            test_error_decorator()
        except Exception as e:
            print(f"Expected error caught: {e}")
        
        print("\\n=== All Discord logging tests completed! ===")
        print("Check your Discord channels for the test messages.")
        
    except Exception as e:
        print(f"Test failed with error: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    main()
