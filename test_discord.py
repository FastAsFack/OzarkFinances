"""
Test Discord Logger
Simple script to test Discord webhook functionality
"""

from discord_logger import discord_logger

def test_discord_webhooks():
    """Test all Discord webhook channels"""
    print("Testing Discord webhooks...")
    
    # Test System Channel
    print("Testing System channel...")
    discord_logger.log_app_startup(version="Test", host="localhost", port=5000)
    
    # Test Finance Channel  
    print("Testing Finance channel...")
    discord_logger.log_invoice_created(invoice_id="TEST001", amount=123.45, client="Test Client")
    
    # Test Error Channel
    print("Testing Error channel...")
    try:
        raise ValueError("This is a test error")
    except Exception as e:
        discord_logger.log_error(e, context="Testing Discord Error Logging")
    
    # Test Activity Channel
    print("Testing Activity channel...")
    discord_logger.log_user_action(action="Discord Test", details={"test": "successful"})
    
    print("All tests completed! Check your Discord channels.")

if __name__ == "__main__":
    test_discord_webhooks()
